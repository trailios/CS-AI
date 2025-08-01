package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"math/rand"
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
	
}

func startProcess(bda string, proxy string, blob string) (int, string, error) {
	fmt.Printf("Starting process for: \nBDA: %s\nPROXY: %s\nBLOB: %s", bda, proxy, blob)

	now := time.Now().Unix()
	esync := strconv.FormatInt(now-(now%21600), 10)

	session := azuretls.NewSession()
	err := session.SetProxy(proxy)
	if err != nil {
		fmt.Println(err)
	}

	session.OrderedHeaders = azuretls.OrderedHeaders{
		{"accept", "*/*"},
		{"accept-language", "en,de-DE;q=0.9,de;q=0.8,en-US;q=0.7"},
		{"cache-control", "no-cache"},
		{"content-type", "application/x-www-form-urlencoded; charset=UTF-8"},
		{"origin", "https://www.roblox.com"},
		{"pragma", "no-cache"},
		{"priority", "u=1, i"},
		{"referer", "https://www.roblox.com/"},
		{"sec-ch-ua", `"Not)A;Brand";v="8", "Chromium";v="138", "Brave";v="138"`},
		{"sec-ch-ua-mobile", "?0"},
		{"sec-ch-ua-platform", `"Windows"`},
		{"sec-fetch-dest", "empty"},
		{"sec-fetch-mode", "cors"},
		{"sec-fetch-site", "same-site"},
		{"sec-gpc", "1"},
		{"user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"},
		{"x-ark-esync-value", esync},
	}
	ja3 := "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53-255,0-11-10-35-5-16-18-23-13-43-45-51-21,29-23-24,0-1-2"
	if err := session.ApplyJa3(ja3, azuretls.Chrome); err != nil {
		panic(err)
	}
	http3 := "1:16383;7:100;GREASE|m,s,a,p"
	if err := session.ApplyHTTP3(http3); err != nil {
		panic(fmt.Sprintf("failed to apply HTTP/3 settings: %v", err))
	}
	randomFloat := strconv.FormatFloat(rand.Float64(), 'f', -1, 64)
	params := []struct{ Key, Value string }{
		{"public_key", "476068BF-9607-4799-B53D-966BE98E2B81"},
		{"capi_version", "3.5.0"},
		{"capi_mode", "inline"},
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
		Url:        "https://arkoselabs.roblox.com/fc/gt2/public_key/476068BF-9607-4799-B53D-966BE98E2B81",
		Body: 		encodedParams,
		ForceHTTP3: true,
	})
	if err != nil {
		panic(err)
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

	statusCode, respBody, err := startProcess(data.BDA, data.Proxy, data.Blob)
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
