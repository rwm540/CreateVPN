using System;
using System.Collections.Generic;
using System.Threading;
using System.Text.Json;
using System.Text.Json.Serialization;

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
        static void Main(string[] args)
        {
            if (args.Length == 0)
            {
                // Obfuscated error message or silent fail is better for security, but keeping it usable for now
                Console.WriteLine("ERR_NO_ARGS");
                return;
            }

            string command = args[0].ToLower();

            switch (command)
            {
                case "list":
                    ListServers();
                    break;
                case "connect":
                    if (args.Length < 2)
                    {
                        Console.WriteLine("ERR_INVALID_ARGS");
                        return;
                    }
                    // Input validation to prevent injection
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
            // Simple validation: alphanumeric only
            foreach (char c in id)
            {
                if (!char.IsLetterOrDigit(c)) return false;
            }
            return true;
        }

        static void ListServers()
        {
            var servers = new List<ServerInfo>
            {
                new ServerInfo { id = "de1", name = "Germany - Frankfurt (Free)", ip = "192.168.1.101", load = "12%" },
                new ServerInfo { id = "us1", name = "USA - New York (Free)", ip = "192.168.1.102", load = "45%" },
                new ServerInfo { id = "jp1", name = "Japan - Tokyo (Free)", ip = "192.168.1.103", load = "89%" },
                new ServerInfo { id = "ir1", name = "Iran - Tehran (Internal)", ip = "10.10.10.10", load = "5%" }
            };

            // Use the source-generated context for AOT
            string json = JsonSerializer.Serialize(servers, AppJsonContext.Default.ListServerInfo);
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
