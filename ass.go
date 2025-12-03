package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"

	azuretls "github.com/Noooste/azuretls-client"
)

type RequestData struct {
	Blob   string `json:"blob"`
	Proxy  string `json:"proxy"`
	BDA    string `json:"bda"`
	SURL   string `json:"url"`
	Pkey   string `json:"public_key"`
	AL     string `json:"accept_language"`
	Cookie string `json:"cookies"`
}

func init() {
	rand.Seed(time.Now().UnixNano())
}

func startProcess(bda, proxy, blob, surl, pkey, al, cookie string) (int, string, error) {
	now := time.Now().UnixMilli()
	rounded := (now / 100) * 100
	esync := strconv.FormatInt(rounded, 10)

	session := azuretls.NewSession()
	if err := session.SetProxy(proxy); err != nil {
		return 0, "", fmt.Errorf("failed to set proxy: %w", err)
	}
	defer session.Close()

	//session.Browser = azuretls.Safari

	session.ApplyJa3("771,4865-4866-4867-49196-49195-52393-49200-49199-52392-49162-49161-49172-49171-157-156-53-47-49160-49170-10,0-23-65281-10-11-16-5-13-18-51-45-43-27-21,29-23-24-25,0", azuretls.Safari)
	session.ApplyHTTP2("2:0;4:4194304;3:100|10485760|0|m,s,p,a")


	randomFloat := strconv.FormatFloat(rand.Float64(), 'f', -1, 64)

	params := []struct {
		Key   string
		Value string
	}{
		{"c", bda},
		{"public_key", pkey},
		{"site", "https://www.roblox.com"},
		{"userbrowser", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15"},
		{"capi_version", "4.0.11"},
		{"capi_mode", "lightbox"},
		{"style_theme", "modal"},
		{"rnd", randomFloat},
		{"data[blob]", blob},
	}

	var parts []string
	for _, p := range params {
		key := url.QueryEscape(p.Key)
		value := url.QueryEscape(p.Value)
		parts = append(parts, key+"="+value)
	}
	encodedParams := strings.Join(parts, "&")
	contentLength := strconv.Itoa(len(encodedParams))

	acceptLanguage := al
	if acceptLanguage == "" {
		acceptLanguage = "de-DE,de;q=0.9"
	}

	session.OrderedHeaders = azuretls.OrderedHeaders{
		{"content-type", "application/x-www-form-urlencoded; charset=UTF-8"},
		{"x-ark-esync-value", esync},
		{"accept", "*/*"},
		{"sec-fetch-site", "same-site"},
		{"accept-language", acceptLanguage},
		{"accept-encoding", "gzip, deflate, br"},
		{"sec-fetch-mode", "cors"},
		{"origin", "https://www.roblox.com"},
		{"content-length", contentLength},
		{"user-agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15"},
		{"ark-build-id", "4e0e9770-e252-4758-8751-980278702a08"},
		{"referer", "https://www.roblox.com/"},
		{"sec-fetch-dest", "empty"},
		{"cookie", cookie},
	}

	resp, err := session.Post(surl, encodedParams)
	if err != nil {
		return 0, "", fmt.Errorf("failed to send request: %w", err)
	}

	fmt.Printf("resp.Body: %v\n", string(resp.Body))

	return resp.StatusCode, string(resp.Body), nil
}

func sendRequestHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Only POST method is allowed", http.StatusMethodNotAllowed)
		return
	}

	var data RequestData
	if err := json.NewDecoder(r.Body).Decode(&data); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	statusCode, respBody, err := startProcess(data.BDA, data.Proxy, data.Blob, data.SURL, data.Pkey, data.AL, data.Cookie)
	if err != nil {
		http.Error(w, fmt.Sprintf("Internal Error: %v", err), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)

	_ = json.NewEncoder(w).Encode(map[string]interface{}{
		"status":  "success",
		"message": "Request completed",
		"body":    respBody,
	})
}

func main() {
	http.HandleFunc("/send-request", sendRequestHandler)
	log.Fatal(http.ListenAndServe(":19222", nil))
}
