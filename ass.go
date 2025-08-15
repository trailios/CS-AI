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

	"github.com/Noooste/azuretls-client"
)

type RequestData struct {
	Blob  string `json:"blob"`
	Proxy string `json:"proxy"`
	BDA   string `json:"bda"`
	SURL  string `json:"url"`
	Pkey  string `json:"public_key"`
	AL    string `json:"accept_language"`
}

func startProcess(bda string, proxy string, blob string, surl string, pkey string, al string) (int, string, error) {

	now := time.Now().Unix()
	esync := strconv.FormatInt(now-(now%21600), 10)

	session := azuretls.NewSession()
	err := session.SetProxy(proxy)
	if err != nil {
		return 0, "", fmt.Errorf("failed to send request: %w", err)
	}

	session.OrderedHeaders = azuretls.OrderedHeaders{
		{"sec-ch-ua-platform", `"Windows"`},
		{"x-ark-esync-value", string(esync)},
		{"user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"},
		{"sec-ch-ua", `"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"`},
		{"content-type", "application/x-www-form-urlencoded; charset=UTF-8"},
		{"sec-ch-ua-mobile", "?0"},
		{"accept", "*/*"},
		{"origin", "https://www.roblox.com"},
		{"accept-language", al},
		{"sec-fetch-site", "same-site"},
		{"sec-fetch-mode", "cors"},
		{"sec-fetch-dest", "empty"},
		{"priority", "u=1, i"},
		{"referer", "https://www.roblox.com/"},
	}
	ja3 := "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,5-65281-23-45-35-11-13-65037-51-27-16-17613-43-0-10-18,4588-29-23-24,0"
	if err := session.ApplyJa3(ja3, azuretls.Chrome); err != nil {
		return 0, "", fmt.Errorf("failed to send request: %w", err)
	}

	
	http3 := "1:65536;6:262144;7:100;51:1;GREASE|m,a,s,p"
	if err := session.ApplyHTTP3(http3); err != nil {
		return 0, "", fmt.Errorf("failed to send request: %w", err)
	}
	randomFloat := strconv.FormatFloat(rand.Float64(), 'f', -1, 64)
	params := []struct{ Key, Value string }{
		{"public_key", pkey},
		{"capi_version", "3.7.0"},
		{"capi_mode", "lightbox"},
		{"style_theme", "default"},
		{"rnd", randomFloat},
		{"bda", bda},
		{"site", "https://www.roblox.com"},
		{"userbrowser", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"},
		{"data[blob]", string(blob)},
	}
	var parts []string
	for _, p := range params {
		key := url.QueryEscape(p.Key)
		value := url.QueryEscape(p.Value)
		parts = append(parts, key+"="+value)
	}
	encodedParams := strings.Join(parts, "&")



	resp, err := session.Do(&azuretls.Request{
		Method:     "POST",
		Url:        surl,
		Body:       encodedParams,
		ForceHTTP3: true,
	})
	if err != nil {
		return 0, "", fmt.Errorf("failed to send request: %w", err)
	}

	fmt.Println(resp.StatusCode)
	fmt.Println(string(resp.Body))
	
	session.Close()
	return resp.StatusCode, string(resp.Body), nil
}

func sendRequestHandler(w http.ResponseWriter, r *http.Request) {
	// Ensure it's a POST request
	if r.Method != http.MethodPost {
		http.Error(w, "Only POST method is allowed", http.StatusMethodNotAllowed)
		return
	}

	var data RequestData

	// Parse JSON body
	err := json.NewDecoder(r.Body).Decode(&data)
	if err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	statusCode, respBody, err := startProcess(data.BDA, data.Proxy, data.Blob, data.SURL, data.Pkey, data.AL)
	if err != nil {
		http.Error(w, fmt.Sprintf("Internal Error: %v", err), http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":  "success",
		"message": "Request completed",
		"body":    respBody,
	})
}

func main() {
	fmt.Println("Starting Server on port 8080...")

	http.HandleFunc("/send-request", sendRequestHandler)

	log.Fatal(http.ListenAndServe(":19222", nil))
}
