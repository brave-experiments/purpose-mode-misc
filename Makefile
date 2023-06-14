executable = backend
godeps = *.go

all: lint $(executable)

.PHONY: lint
lint: $(godeps)
	golangci-lint run

$(executable): $(godeps)
	go build -o $(executable)

.PHONY: clean
clean:
	rm -f $(executable)
