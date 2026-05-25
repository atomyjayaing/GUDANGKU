import { Suspense } from "react";
import { LoginForm } from "./login-form";

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold tracking-tight">SJE POS</h1>
          <p className="text-sm text-slate-500 mt-1">
            Login untuk mengelola toko Anda
          </p>
        </div>
        <Suspense fallback={<div className="text-sm text-slate-400">Memuat...</div>}>
          <LoginForm />
        </Suspense>
        <p className="mt-6 text-xs text-slate-400 text-center">
          Default: <span className="font-mono">admin@sje.local</span> /{" "}
          <span className="font-mono">admin123</span>
        </p>
      </div>
    </div>
  );
}
