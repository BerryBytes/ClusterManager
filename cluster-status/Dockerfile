# Stage 1: Build the application
FROM golang:1.19 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY *.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -o main

FROM alpine:3.18
WORKDIR /app
COPY --from=builder /app/main .
CMD ["./main"]              