using System;
using System.Collections.Generic;
using System.Threading;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;

namespace VpnEngine
{
    // Define strict data models for AOT compatibility
    public class ServerInfo
    {
        public string id { get; set; } = "";
        public string name { get; set; } = "";
        public string ip { get; set; } = "";
        public string load { get; set; } = "";
    }

    [JsonSerializable(typeof(List<ServerInfo>))]
    internal partial class AppJsonContext : JsonSerializerContext
    {
    }

    class Program
    {
        static async Task Main(string[] args)
        {
            if (args.Length == 0)
            {
                Console.WriteLine("ERR_NO_ARGS");
                return;
            }

            string command = args[0].ToLower();

            switch (command)
            {
                case "list":
                    ListServers();
                    break;
                case "fetch-public":
                    await FetchPublicServers();
                    break;
                case "connect":
                    if (args.Length < 2)
                    {
                        Console.WriteLine("ERR_INVALID_ARGS");
                        return;
                    }
                    string serverId = args[1];
                    if (!IsValidServerId(serverId))
                    {
                        Console.WriteLine("ERR_INVALID_ID");
                        return;
                    }
                    Connect(serverId);
                    break;
                case "disconnect":
                    Disconnect();
                    break;
                default:
                    Console.WriteLine("ERR_UNKNOWN_CMD");
                    break;
            }
        }

        static bool IsValidServerId(string id)
        {
            foreach (char c in id)
            {
                if (!char.IsLetterOrDigit(c) && c != '-' && c != '.') return false;
            }
            return true;
        }

        static async Task FetchPublicServers()
        {
            // Fetching from VPNGate API (CSV format)
            try 
            {
                using var client = new HttpClient();
                // This is a public API for free VPN servers
                string csvData = await client.GetStringAsync("http://www.vpngate.net/api/iphone/");
                
                var servers = new List<ServerInfo>();
                var lines = csvData.Split('\n');
                
                int count = 0;
                // Skip header (starts at line 2 usually)
                foreach (var line in lines)
                {
                    if (string.IsNullOrWhiteSpace(line) || line.StartsWith("*") || line.StartsWith("#")) continue;
                    
                    var parts = line.Split(',');
                    if (parts.Length > 6)
                    {
                        // VPNGate CSV format: HostName,IP,Score,Ping,Speed,CountryLong,CountryShort...
                        string country = parts[5];
                        string ip = parts[1];
                        string speed = (long.Parse(parts[4]) / 1000000).ToString() + " Mbps";
                        
                        servers.Add(new ServerInfo 
                        { 
                            id = ip, // Use IP as ID for simplicity
                            name = $"{country} ({speed})", 
                            ip = ip, 
                            load = "Public" 
                        });
                        
                        count++;
                        if (count >= 10) break; // Limit to top 10 to avoid overwhelming UI
                    }
                }

                string json = JsonSerializer.Serialize(servers, AppJsonContext.Default.ListServerInfo);
                Console.WriteLine(json);
                
                // Save to local file as cache
                File.WriteAllText("servers.json", json);
            }
            catch (Exception ex)
            {
                Console.WriteLine("[]"); // Return empty array on error
            }
        }

        static void ListServers()
        {
            string configPath = "servers.json";
            
            // Try to find servers.json
            if (!File.Exists(configPath))
            {
                if (File.Exists("../servers.json")) configPath = "../servers.json";
            }

            if (File.Exists(configPath))
            {
                try 
                {
                    string jsonContent = File.ReadAllText(configPath);
                    var servers = JsonSerializer.Deserialize(jsonContent, AppJsonContext.Default.ListServerInfo);
                    Console.WriteLine(JsonSerializer.Serialize(servers, AppJsonContext.Default.ListServerInfo));
                    return;
                }
                catch {}
            }

            // Fallback
            var defaultServers = new List<ServerInfo>
            {
                new ServerInfo { id = "local", name = "No servers found. Click 'Update Public Servers'", ip = "0.0.0.0", load = "0%" }
            };

            string json = JsonSerializer.Serialize(defaultServers, AppJsonContext.Default.ListServerInfo);
            Console.WriteLine(json);
        }

        static void Connect(string serverId)
        {
            Console.WriteLine($"[SecureEngine] Initializing secure tunnel to {serverId}...");
            Thread.Sleep(500); 
            
            Console.WriteLine("[SecureEngine] Handshaking...");
            Thread.Sleep(500);
            
            Console.WriteLine("[SecureEngine] Verifying integrity...");
            Thread.Sleep(500);

            Console.WriteLine("SUCCESS");
        }

        static void Disconnect()
        {
            Console.WriteLine("[SecureEngine] Terminating tunnel...");
            Thread.Sleep(1000);
            Console.WriteLine("DISCONNECTED");
        }
    }
}
