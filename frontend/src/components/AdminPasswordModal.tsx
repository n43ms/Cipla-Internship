import React, { useState } from "react";
import { Key, X, CheckCircle, AlertCircle, Lock } from "lucide-react";
import { apiPost } from "../api/client";

interface AdminPasswordModalProps {
  isOpen: boolean;
  onClose: () => void;
  adminEmail: string;
}

interface ChangePasswordResponse {
  success: boolean;
  message: string;
}

export function AdminPasswordModal({ isOpen, onClose, adminEmail }: AdminPasswordModalProps) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [statusMsg, setStatusMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatusMsg(null);

    if (newPassword !== confirmPassword) {
      setStatusMsg({ type: "error", text: "New password and confirmation do not match." });
      return;
    }

    if (newPassword.length < 6) {
      setStatusMsg({ type: "error", text: "New password must be at least 6 characters long." });
      return;
    }

    setSubmitting(true);
    try {
      const res = await apiPost<ChangePasswordResponse, { admin_email: string; current_password: string; new_password: string }>(
        "/api/auth/change-password",
        {
          admin_email: adminEmail,
          current_password: currentPassword,
          new_password: newPassword,
        }
      );

      if (res.success) {
        setStatusMsg({ type: "success", text: "Active passcode for @cipla.com users updated successfully!" });
        setCurrentPassword("");
        setNewPassword("");
        setConfirmPassword("");
        setTimeout(() => {
          onClose();
          setStatusMsg(null);
        }, 1800);
      }
    } catch (err: any) {
      const detail = err.detail || err.message || "";
      if (detail.includes("403") || detail.toLowerCase().includes("designated") || detail.toLowerCase().includes("authorized")) {
        setStatusMsg({ type: "error", text: "403 Forbidden: Only designated administrators can change passcodes." });
      } else if (detail.includes("401") || detail.toLowerCase().includes("incorrect")) {
        setStatusMsg({ type: "error", text: "401 Unauthorized: Current admin passcode is incorrect." });
      } else {
        setStatusMsg({ type: "error", text: detail || "Failed to update passcode. Please verify credentials." });
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[120] flex items-center justify-center bg-black/80 p-4 backdrop-blur-md">
      <div className="relative w-full max-w-md overflow-hidden rounded-2xl border border-white/10 bg-[#121417] p-6 shadow-2xl">
        <div className="flex items-center justify-between border-b border-white/[0.08] pb-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-amber-400/30 bg-amber-500/10 text-amber-300">
              <Key className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-zinc-100">Reset Admin Passcode</h3>
              <p className="text-xs text-zinc-400">Update active passcode for @cipla.com users</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-zinc-400 hover:bg-white/[0.06] hover:text-zinc-200"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {statusMsg && (
          <div
            className={`mt-4 flex items-center gap-2.5 rounded-lg border p-3 text-xs font-medium ${
              statusMsg.type === "success"
                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
                : "border-rose-500/30 bg-rose-500/10 text-rose-300"
            }`}
          >
            {statusMsg.type === "success" ? (
              <CheckCircle className="h-4 w-4 shrink-0 text-emerald-400" />
            ) : (
              <AlertCircle className="h-4 w-4 shrink-0 text-rose-400" />
            )}
            <span>{statusMsg.text}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1">Admin Account</label>
            <input
              type="text"
              disabled
              value={adminEmail}
              className="w-full rounded-lg border border-white/[0.08] bg-black/40 px-3.5 py-2.5 text-xs text-zinc-400 cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1">Current Passcode</label>
            <input
              type="password"
              required
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              placeholder="Enter current passcode"
              className="w-full rounded-lg border border-white/10 bg-black/30 px-3.5 py-2.5 text-xs text-zinc-100 placeholder-zinc-500 focus:border-amber-400/50 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1">New Passcode</label>
            <input
              type="password"
              required
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Enter new passcode"
              className="w-full rounded-lg border border-white/10 bg-black/30 px-3.5 py-2.5 text-xs text-zinc-100 placeholder-zinc-500 focus:border-amber-400/50 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-zinc-300 mb-1">Confirm New Passcode</label>
            <input
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm new passcode"
              className="w-full rounded-lg border border-white/10 bg-black/30 px-3.5 py-2.5 text-xs text-zinc-100 placeholder-zinc-500 focus:border-amber-400/50 focus:outline-none"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-3">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-white/10 bg-transparent px-4 py-2.5 text-xs font-semibold text-zinc-300 hover:bg-white/[0.05]"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex items-center gap-2 rounded-lg border border-amber-400/30 bg-amber-500/20 px-4 py-2.5 text-xs font-semibold text-amber-200 hover:bg-amber-500/30 disabled:opacity-50"
            >
              <Lock className="h-3.5 w-3.5" />
              {submitting ? "Updating..." : "Update Passcode"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
