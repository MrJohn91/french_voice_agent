"use client";

import { useState, useCallback } from "react";
import { Orb, type AgentState } from "@/components/ui/orb";
import { VoiceCallInterface } from "@/components/voice-call-interface";
import { Mic, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export default function Home() {
  const [agentState, setAgentState] = useState<AgentState>(null);
  const [isCallActive, setIsCallActive] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [serverUrl, setServerUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const startCall = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await fetch("/api/token?roomName=french-agent-room&participantName=User");
      const data = await response.json();

      if (data.token && data.serverUrl) {
        setToken(data.token);
        setServerUrl(data.serverUrl);
        setIsCallActive(true);
      } else {
        console.error("Failed to get token", data);
      }
    } catch (error) {
      console.error("Error fetching token:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleDisconnect = useCallback(() => {
    setIsCallActive(false);
    setToken(null);
    setAgentState(null);
  }, []);

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-background via-background to-secondary overflow-hidden relative">
      {/* Background Ambient Effects */}
      <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-[100px] pointer-events-none" />

      {/* Header */}
      <header className="fixed top-0 w-full p-6 flex justify-between items-center z-50 bg-background/80 backdrop-blur-md border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-blue-500 animate-pulse shadow-[0_0_10px_rgba(59,130,246,0.5)]" />
          <h1 className="text-xl font-bold tracking-tight text-white">
            French Voice Agent
          </h1>
        </div>
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-white/70">
          <a href="#features" className="hover:text-white transition-colors">Features</a>
          <a href="#how-it-works" className="hover:text-white transition-colors">How it Works</a>
          <a href="#benefits" className="hover:text-white transition-colors">Benefits</a>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="relative w-full min-h-screen flex flex-col items-center justify-center pt-20 px-4">
        <div className="text-center mb-12 max-w-3xl z-10">
          <h2 className="text-4xl md:text-6xl font-bold text-white mb-6 tracking-tight">
            Intelligent Bilingual <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-300 via-blue-500 to-purple-600">
              Voice Assistant
            </span>
          </h2>
          <p className="text-lg md:text-xl text-white/60 mb-8 leading-relaxed">
            Handle appointment bookings automatically in French and English.
            Available 24/7 to manage your calendar and provide professional customer service.
          </p>

          {/* Orb Container */}
          <div className="w-full max-w-[500px] h-[300px] md:h-[400px] relative flex items-center justify-center mb-8 mx-auto">
            <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500/10 via-purple-500/10 to-transparent rounded-full blur-3xl" />
            <Orb
              agentState={agentState}
              colors={["#06b6d4", "#8b5cf6"]}
              className="w-full h-full z-10 opacity-90"
            />
          </div>

          {/* Status Text */}
          <div className="h-8 flex items-center justify-center z-10 mb-8">
            {agentState === "listening" && (
              <p className="text-blue-300 font-medium animate-pulse flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-300" /> Listening...
              </p>
            )}
            {agentState === "talking" && (
              <p className="text-purple-300 font-medium animate-pulse flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-purple-300" /> Speaking...
              </p>
            )}
            {agentState === "thinking" && (
              <p className="text-white/60 font-medium animate-pulse flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-white/60" /> Thinking...
              </p>
            )}
          </div>

          {/* Start Button */}
          {!isCallActive && (
            <button
              onClick={startCall}
              disabled={isLoading}
              className={cn(
                "group relative px-6 py-3 bg-blue-900/50 hover:bg-blue-800/50 text-white rounded-full transition-all duration-300 ease-out border border-blue-500/30 backdrop-blur-sm",
                "hover:scale-105 hover:border-blue-400/50 hover:shadow-[0_0_20px_rgba(59,130,246,0.2)]",
                "active:scale-95",
                isLoading && "opacity-50 cursor-not-allowed"
              )}
            >
              <div className="flex items-center gap-2 text-sm">
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Mic className="w-4 h-4 text-blue-300" />
                )}
                <span className="font-medium tracking-wide text-blue-100">
                  {isLoading ? "Connecting..." : "Talk to Agent"}
                </span>
              </div>
            </button>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="w-full py-24 px-4 bg-black/20 relative z-10">
        <div className="max-w-6xl mx-auto">
          <h3 className="text-3xl font-bold text-white mb-16 text-center">Key Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                title: "Bilingual Conversations",
                description: "Seamlessly switches between French and English based on the customer's language preference.",
                icon: "🗣️"
              },
              {
                title: "Smart Calendar",
                description: "Real-time availability checking and automatic conflict detection with Google Calendar.",
                icon: "📅"
              },
              {
                title: "24/7 Availability",
                description: "Never miss a call. The agent handles unlimited simultaneous conversations day and night.",
                icon: "🌙"
              }
            ].map((feature, i) => (
              <div key={i} className="p-8 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h4 className="text-xl font-semibold text-white mb-3">{feature.title}</h4>
                <p className="text-white/60 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="w-full py-24 px-4 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          <h3 className="text-3xl font-bold text-white mb-16">How It Works</h3>
          <div className="flex flex-col md:flex-row items-center justify-between gap-8 relative">
            {/* Connecting Line */}
            <div className="hidden md:block absolute top-1/2 left-0 w-full h-0.5 bg-gradient-to-r from-blue-500/0 via-blue-500/50 to-blue-500/0 -translate-y-1/2" />

            {[
              { step: "1", text: "Customer Calls" },
              { step: "2", text: "Natural Chat" },
              { step: "3", text: "Checks Calendar" },
              { step: "4", text: "Books Slot" },
              { step: "5", text: "Sends Confirmation" }
            ].map((item, i) => (
              <div key={i} className="relative z-10 flex flex-col items-center gap-4 bg-background p-4 rounded-xl border border-white/5">
                <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-blue-900/50">
                  {item.step}
                </div>
                <p className="text-white font-medium">{item.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section id="benefits" className="w-full py-24 px-4 bg-gradient-to-b from-blue-900/20 to-transparent relative z-10">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
            <div>
              <h3 className="text-3xl font-bold text-white mb-6">Strategic Cost Efficiency</h3>
              <p className="text-white/60 text-lg mb-8">
                Traditional staffing costs over <strong>$75,000 annually</strong> per position when accounting for salary, benefits, and training.
                Our voice agent eliminates these overheads while delivering superior performance.
              </p>
              <div className="space-y-6">
                <div>
                  <h4 className="text-white font-semibold mb-3">Voice Agent Benefits</h4>
                  <ul className="space-y-2">
                    {[
                      "24/7 Availability - 3x more bookings outside business hours",
                      "95% Booking Accuracy vs 70-80% human error rate",
                      "Instant Multi-language - French/English automatic switching",
                      "Zero Sick Days - Consistent service quality",
                      "Scalable - Handle unlimited concurrent calls"
                    ].map((item, i) => (
                      <li key={i} className="flex items-center gap-3 text-white/80 text-sm">
                        <div className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="text-white font-semibold mb-3">Business Impact Metrics</h4>
                  <ul className="space-y-2">
                    {[
                      "Never Miss a Booking: Capture leads 24/7",
                      "Reduce No-Shows: Automated reminders and confirmations",
                      "Increase Revenue: More bookings = higher utilization",
                      "Staff Efficiency: Free human staff for high-value tasks"
                    ].map((item, i) => (
                      <li key={i} className="flex items-center gap-3 text-white/80 text-sm">
                        <div className="w-1.5 h-1.5 rounded-full bg-purple-400" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-6 rounded-2xl bg-white/5 border border-white/10 text-center">
                <div className="text-3xl font-bold text-green-400 mb-2">$75k</div>
                <div className="text-sm text-white/60">Annual Savings/Role</div>
              </div>
              <div className="p-6 rounded-2xl bg-white/5 border border-white/10 text-center">
                <div className="text-3xl font-bold text-purple-400 mb-2">3x</div>
                <div className="text-sm text-white/60">After-hours Bookings</div>
              </div>
              <div className="p-6 rounded-2xl bg-white/5 border border-white/10 text-center">
                <div className="text-3xl font-bold text-blue-400 mb-2">95%</div>
                <div className="text-sm text-white/60">Booking Accuracy</div>
              </div>
              <div className="p-6 rounded-2xl bg-white/5 border border-white/10 text-center">
                <div className="text-3xl font-bold text-orange-400 mb-2">∞</div>
                <div className="text-sm text-white/60">Concurrent Calls</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="w-full py-12 px-4 border-t border-white/10 relative z-10 bg-black/40">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="text-white/40 text-sm">
            © 2024 French Voice Agent. All rights reserved.
          </div>
          <div className="flex gap-6 text-white/40 text-sm">
            <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-white transition-colors">Contact</a>
          </div>
        </div>
      </footer>

      {/* Voice Interface (Overlay) */}
      {isCallActive && token && serverUrl && (
        <VoiceCallInterface
          token={token}
          serverUrl={serverUrl}
          roomName="french-agent-room"
          onStateChange={setAgentState}
          onDisconnect={handleDisconnect}
        />
      )}
    </main>
  );
}
