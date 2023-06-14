package main

import (
	"crypto/tls"
	"errors"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path"
	"time"

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

func writeToDisk(dir string, blob []byte) error {
	fileName := time.Now().UTC().Format(time.RFC3339Nano)
	fullPath := path.Join(dir, fileName)

	fd, err := os.Create(fullPath)
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
			http.Error(w, errFailedToWrite.Error(), http.StatusInternalServerError)
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
		Handler: r,
		Addr:    fmt.Sprintf(":%d", port),
		TLSConfig: &tls.Config{
			GetCertificate: certManager.GetCertificate,
		},
	}

	l.Fatal(srv.ListenAndServeTLS("", ""))
}
