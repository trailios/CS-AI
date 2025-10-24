package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math"
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


func randomChoicesWithReplacementThenDedup(values []string, min, max int) []string {
	// Python's randint(a, b) is inclusive for both ends
	randCount := rand.Intn(max-min+1) + min

	// Pick with replacement
	picks := make([]string, randCount)
	for i := 0; i < randCount; i++ {
		picks[i] = values[rand.Intn(len(values))]
	}

	// Deduplicate like Python's set()
	unique := make(map[string]struct{})
	for _, v := range picks {
		unique[v] = struct{}{}
	}

	// Convert back to slice
	result := make([]string, 0, len(unique))
	for k := range unique {
		result = append(result, k)
	}
	return result
}


func startProcess(bda string, proxy string, blob string, surl string, pkey string, al string) (int, string, error) {

	now := time.Now().UnixMilli()
    rounded := int64(math.Round(float64(now)/100) * 100)
    esync :=strconv.FormatInt(rounded, 10)
	fmt.Printf("esync: %v\n", esync)

	session := azuretls.NewSession()
	err := session.SetProxy(proxy)
	if err != nil {
		return 0, "", fmt.Errorf("failed to send request: %w", err)
	}

	session.OrderedHeaders = azuretls.OrderedHeaders{
		{"sec-ch-ua-platform", `"Windows"`},
		{"x-ark-esync-value", string(esync)},
		{"ark-build-id", "c1e346ea-955c-4367-98a1-4029e512358f"},
		{"user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"},
		{"sec-ch-ua", `"Google Chrome";v="141", "Not)A;Brand";v="8", "Chromium";v="141"`},
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

	rand.Seed(time.Now().UnixNano())

	// groupsList := []string{"29", "23", "24", "25"}
	// cipherList := []string{
	// 	"47", "53", "60", "61", "140", "141", "156", "157",
	// 	"49161", "49162", "49171", "49172", "49187", "49188",
	// 	"49191", "49192", "49195", "49196", "49199", "49200",
	// 	"49205", "49206", "52392", "52393", "52396",
	// 	"4865", "4866", "4867",
	// }

	// supportedGroups := strings.Join(randomChoicesWithReplacementThenDedup(groupsList, 1, 3), "-")
	// ciphers := strings.Join(randomChoicesWithReplacementThenDedup(cipherList, 12, 28), "-")

	ja3 := "771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,16-11-13-23-10-51-43-27-18-5-17613-45-35-0-65281-65037,4588-29-23-24,0"
	if err := session.ApplyJa3(ja3, azuretls.Chrome); err != nil {
		return 0, "", fmt.Errorf("failed to send request: %w", err)
	}

	http2 := "1:65536;2:0;4:6291456;6:262144|15663105|0|m,a,s,p"
	
	if err := session.ApplyHTTP2(http2); err != nil {
		return 0, "", fmt.Errorf("failed to send request: %w", err)
	}

	http3 := "1:65536;6:262144;7:100;51:1;GREASE|m,a,s,p"
	if err := session.ApplyHTTP3(http3); err != nil {
		return 0, "", fmt.Errorf("failed to send request: %w", err)
	}
	randomFloat := strconv.FormatFloat(rand.Float64(), 'f', -1, 64)
	params := []struct{ Key, Value string }{
		{"c", bda},
		{"public_key", pkey},
		{"site", "https://www.roblox.com"},
		{"userbrowser", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"},
		{"capi_version", "4.0.10"},
		{"capi_mode", "lightbox"},
		{"style_theme", "modal"},
		{"rnd", randomFloat},
		{"data[blob]", string(blob)},
	}
	var parts []string
	for _, p := range params {
		key := url.QueryEscape(p.Key)
		value := url.QueryEscape(p.Value)
		parts = append(parts, key+"="+value)
	}
	encodedParams := strings.Join(parts, "&")

	// resp, err := session.Post(surl, encodedParams)

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
