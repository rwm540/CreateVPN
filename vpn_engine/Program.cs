using System;
using System.Collections.Generic;
using System.Threading;
using System.Text.Json;

namespace VpnEngine
{
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length == 0)
            {
                Console.WriteLine("Usage: vpn_engine [list|connect <server_id>|disconnect]");
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
                        Console.WriteLine("Error: Server ID required.");
                        return;
                    }
                    Connect(args[1]);
                    break;
                case "disconnect":
                    Disconnect();
                    break;
                default:
                    Console.WriteLine("Unknown command.");
                    break;
            }
        }

        static void ListServers()
        {
            // In a real app, this would fetch from an API or scrape a site like VPNGate
            var servers = new List<object>
            {
                new { id = "de1", name = "Germany - Frankfurt (Free)", ip = "192.168.1.101", load = "12%" },
                new { id = "us1", name = "USA - New York (Free)", ip = "192.168.1.102", load = "45%" },
                new { id = "jp1", name = "Japan - Tokyo (Free)", ip = "192.168.1.103", load = "89%" },
                new { id = "ir1", name = "Iran - Tehran (Internal)", ip = "10.10.10.10", load = "5%" }
            };

            string json = JsonSerializer.Serialize(servers);
            Console.WriteLine(json);
        }

        static void Connect(string serverId)
        {
            Console.WriteLine($"[C# Backend] Initializing connection to {serverId}...");
            Thread.Sleep(500); // Simulate setup
            
            Console.WriteLine("[C# Backend] Configuring network interface...");
            Thread.Sleep(500);
            
            Console.WriteLine("[C# Backend] Authenticating...");
            Thread.Sleep(500);

            // Simulate success
            Console.WriteLine("SUCCESS");
        }

        static void Disconnect()
        {
            Console.WriteLine("[C# Backend] Disconnecting...");
            Thread.Sleep(1000);
            Console.WriteLine("DISCONNECTED");
        }
    }
}
