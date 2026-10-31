"use client";

import React, { useEffect, useCallback } from "react";
import { Trophy, Award, Sparkles, X, ExternalLink } from "lucide-react";

interface WinnerModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const WinnerModal: React.FC<WinnerModalProps> = ({ isOpen, onClose }) => {
  const triggerConfetti = useCallback(async () => {
    if (typeof window === "undefined") return;
    try {
      const confetti = (await import("canvas-confetti")).default;
      // Left burst
      confetti({
        particleCount: 70,
        angle: 60,
        spread: 55,
        origin: { x: 0.1, y: 0.7 },
        colors: ["#f59e0b", "#10b981", "#3b82f6", "#ec4899", "#8b5cf6"],
      });
      // Right burst
      confetti({
        particleCount: 70,
        angle: 120,
        spread: 55,
        origin: { x: 0.9, y: 0.7 },
        colors: ["#f59e0b", "#10b981", "#3b82f6", "#ec4899", "#8b5cf6"],
      });
      // Center burst
      setTimeout(() => {
        confetti({
          particleCount: 60,
          spread: 100,
          origin: { x: 0.5, y: 0.4 },
          colors: ["#fbbf24", "#38bdf8", "#34d399", "#f43f5e"],
        });
      }, 250);
    } catch (e) {
      // Graceful fallback
    }
  }, []);

  useEffect(() => {
    if (isOpen) {
      triggerConfetti();
    }
  }, [isOpen, triggerConfetti]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-lg clay-cushion-cream rounded-3xl p-6 sm:p-8 shadow-2xl border border-amber-300/60 overflow-hidden transform transition-all scale-100"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Glow backdrop behind modal */}
        <div className="absolute -top-16 -right-16 w-44 h-44 bg-amber-400/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-16 -left-16 w-44 h-44 bg-cyan-400/20 rounded-full blur-3xl pointer-events-none" />

        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-stone-500 hover:text-stone-800 rounded-full hover:bg-stone-200/50 transition-colors"
          title="Close celebration"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header with Trophy SVG */}
        <div className="flex flex-col items-center text-center">
          <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-gradient-to-tr from-amber-400 to-yellow-200 p-0.5 shadow-[0_8px_20px_-4px_rgba(245,158,11,0.5)] flex items-center justify-center mb-3 sm:mb-4 animate-bounce">
            <div className="w-full h-full rounded-full bg-amber-50 flex items-center justify-center border-2 border-amber-300">
              <Trophy className="w-9 h-9 sm:w-11 sm:h-11 text-amber-600 drop-shadow-sm" />
            </div>
          </div>

          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-amber-100/80 border border-amber-300 text-amber-900 text-xs font-bold mb-2">
            <Sparkles className="w-3.5 h-3.5 text-amber-600" />
            <span>MLH Hacktoberfest Hack Day Ahmedabad 2026</span>
          </div>

          <h2 className="text-2xl sm:text-3xl font-black text-[#2e262f] tracking-tight mb-1">
            🎉 We Won 1st Place! 🎉
          </h2>
          <p className="text-xs sm:text-sm text-stone-600 max-w-sm mb-5">
            <strong>AEGENTRIX</strong> secured the championship title across open-source security and next-gen AI governance!
          </p>

          {/* Awards Badges Grid */}
          <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-2.5 mb-5 text-left">
            <div className="flex items-center space-x-2.5 p-3 rounded-2xl bg-white/70 border border-amber-200 shadow-sm">
              <div className="p-2 rounded-xl bg-amber-100 text-amber-700">
                <Trophy className="w-5 h-5" />
              </div>
              <div>
                <div className="text-[10px] uppercase tracking-wider text-amber-800 font-bold">Grand Prize</div>
                <div className="text-xs font-black text-stone-800">1st Place Overall</div>
              </div>
            </div>

            <div className="flex items-center space-x-2.5 p-3 rounded-2xl bg-white/70 border border-purple-200 shadow-sm">
              <div className="p-2 rounded-xl bg-purple-100 text-purple-700">
                <Award className="w-5 h-5" />
              </div>
              <div>
                <div className="text-[10px] uppercase tracking-wider text-purple-800 font-bold">Category Award</div>
                <div className="text-xs font-black text-stone-800">Best Use of Gemma</div>
              </div>
            </div>

            <div className="sm:col-span-2 flex items-center space-x-2.5 p-3 rounded-2xl bg-white/70 border border-emerald-200 shadow-sm">
              <div className="p-2 rounded-xl bg-emerald-100 text-emerald-700">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <div className="text-[10px] uppercase tracking-wider text-emerald-800 font-bold">Open-Source Track</div>
                <div className="text-xs font-black text-stone-800">Best Open-Source AI Project</div>
              </div>
            </div>
          </div>

          {/* Team Credits with Verified GitHub Handles */}
          <div className="w-full text-center text-xs text-stone-600 mb-6 bg-stone-100/80 py-2.5 px-3 rounded-2xl border border-stone-200/80">
            <span className="text-[10.5px] font-bold text-stone-500 uppercase tracking-wider block mb-1.5">
              Engineered by Team Cipher-Coders
            </span>
            <div className="flex flex-wrap items-center justify-center gap-2 text-xs">
              <a
                href="https://github.com/Cipher-Shadow-IR"
                target="_blank"
                rel="noopener noreferrer"
                className="font-bold text-stone-800 hover:text-amber-700 underline underline-offset-2 decoration-stone-300 transition-colors"
              >
                Ishaan Ray
              </a>
              <span className="text-stone-400">•</span>
              <a
                href="https://github.com/Rishi-prajapati-git"
                target="_blank"
                rel="noopener noreferrer"
                className="font-bold text-stone-800 hover:text-amber-700 underline underline-offset-2 decoration-stone-300 transition-colors"
              >
                Rishi Prajapati
              </a>
              <span className="text-stone-400">•</span>
              <a
                href="https://github.com/Urvi2946"
                target="_blank"
                rel="noopener noreferrer"
                className="font-bold text-stone-800 hover:text-amber-700 underline underline-offset-2 decoration-stone-300 transition-colors"
              >
                Urvi Rathod
              </a>
            </div>
          </div>

          {/* Actions */}
          <div className="w-full flex flex-col sm:flex-row gap-2.5">
            <a
              href="https://www.mlh.com/events/hacktoberfest-hack-day-ahmedabad-x-navracommunity/submissions"
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 py-2.5 px-4 rounded-full bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-white font-bold text-xs sm:text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center space-x-1.5"
            >
              <span>View Official Submission</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>

            <button
              type="button"
              onClick={triggerConfetti}
              className="py-2.5 px-4 rounded-full bg-white hover:bg-stone-50 text-stone-700 font-bold text-xs sm:text-sm border border-stone-300 shadow-sm transition-all"
            >
              More Confetti! 🎊
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
