package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path"
	"syscall"

	"github.com/go-chi/chi"
	"github.com/go-chi/chi/middleware"
	"golang.org/x/crypto/acme/autocert"
)

const landingPage = `
<!doctype html>
<html lang="en">
  <body>
  <p>
    This Web service serves as the backend for the Purpose Mode research study.
  </p>
  <p>
    Contact phw@brave.com for details.
  </p>
  </body>
</html>
`

var (
	l                = log.New(os.Stderr, "backend: ", log.Ldate|log.Ltime|log.LUTC|log.Lshortfile)
	errFailedToWrite = errors.New("failed to write submission to disk")
)

// createFilePath creates and returns a directory path if it doesn't exist yet.
func createFilePath(dir string, blob []byte) (string, error) {
	uid, err := extractUID(blob)
	if err != nil {
		return "", fmt.Errorf("error extracting UID from JSON: %v", err)
	}
	msgType, err := extractType(blob)
	if err != nil {
		return "", fmt.Errorf("error extracting type from JSON: %v", err)
	}

	fileName := msgType + ".json"
	dirPath := path.Join(dir, uid)
	fullPath := path.Join(dirPath, fileName)

	// Create directories if they don't exist already.
	if err := os.MkdirAll(dirPath, 0777); err != nil {
		return "", fmt.Errorf("error creating directories: %v", err)
	}

	return fullPath, nil
}

// writeToDisk writes a submission from the extension to disk.
func writeToDisk(dir string, blob []byte) error {
	fullPath, err := createFilePath(dir, blob)
	if err != nil {
		return err
	}

	fd, err := os.OpenFile(fullPath, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0666)
	if err != nil {
		return err
	}

	// Add a newline if necessary.
	if blob[len(blob)-1] != '\n' {
		blob = append(blob, '\n')
	}

	n, err := fd.Write(blob)
	if err != nil {
		return err
	}
	if n != len(blob) {
		return errors.New("failed to write entire blob to file")
	}
	l.Printf("Wrote submission to: %s", fullPath)

	return nil
}

func extractType(jsonBlob []byte) (string, error) {
	m := struct {
		Type string `json:"type"`
	}{}
	err := json.Unmarshal(jsonBlob, &m)
	if err != nil {
		return "", err
	}
	return m.Type, nil
}

func extractUID(jsonBlob []byte) (string, error) {
	m := struct {
		UID string `json:"uid"`
	}{}
	err := json.Unmarshal(jsonBlob, &m)
	if err != nil {
		return "", err
	}
	return m.UID, nil
}

func indexHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprint(w, landingPage)
}

func getSubmitHandler(dir string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		body, err := io.ReadAll(r.Body)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		if err := writeToDisk(dir, body); err != nil {
			http.Error(w, fmt.Sprintf("%v: %v", errFailedToWrite, err), http.StatusInternalServerError)
			return
		}
	}
}

func main() {
	var dir, fqdn string
	var port uint

	flag.StringVar(&fqdn, "fqdn", "", "Fully qualified domain name.")
	flag.StringVar(&dir, "directory", ".", "Directory to write submissions to.")
	flag.UintVar(&port, "port", 443, "Port for the Web server to listen on.")
	flag.Parse()

	if fqdn == "" {
		l.Fatalln("Flag -fqdn is required.")
	}

	// Reset umask, to get the file and directory permissions we want.
	l.Printf("Set umask from %#o to 0.", syscall.Umask(0))

	r := chi.NewRouter()
	r.Use(middleware.RequestID)
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)

	r.Get("/", indexHandler)
	r.Post("/submit", getSubmitHandler(dir))
	l.Println("Starting Web server.")

	certManager := autocert.Manager{
		Email:      "phw@brave.com",
		Cache:      autocert.DirCache(dir),
		Prompt:     autocert.AcceptTOS,
		HostPolicy: autocert.HostWhitelist([]string{fqdn}...),
	}

	srv := &http.Server{
		Handler:   r,
		Addr:      fmt.Sprintf(":%d", port),
		TLSConfig: certManager.TLSConfig(),
	}

	l.Fatal(srv.ListenAndServeTLS("", ""))
}
