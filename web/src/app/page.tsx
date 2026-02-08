"use client";

import { useCallback, useState } from "react";

type StepStatus = "idle" | "running" | "done" | "error";

const STEP_LABELS = [
  { short: "構造抽出", desc: "PyMuPDFでテキスト・画像・座標をJSONとして抽出" },
  { short: "レイアウト解析", desc: "ヒューリスティック + LLM(オプション)でタイトル・箇条書き等を判定" },
  { short: "PPTX構築", desc: "python-pptxで同じ位置にテキストボックス・図を配置" },
] as const;

function StepIndicator({
  stepIndex,
  status,
  label,
  description,
}: {
  stepIndex: number;
  status: StepStatus;
  label: string;
  description: string;
}) {
  const statusIcon =
    status === "done"
      ? "✓"
      : status === "error"
        ? "!"
        : status === "running"
          ? "⋯"
          : stepIndex + 1;
  const ringColor =
    status === "done"
      ? "ring-success bg-success-soft"
      : status === "error"
        ? "ring-error bg-error-soft"
        : status === "running"
          ? "ring-accent bg-accent-soft/50 animate-pulse"
          : "ring-border bg-surface";

  return (
    <div className="flex flex-col items-center text-center">
      <div
        className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full ring-2 ${ringColor} font-semibold text-foreground`}
        title={description}
      >
        {statusIcon}
      </div>
      <span className="mt-2 text-sm font-medium text-foreground">
        {label}
      </span>
      <span className="mt-0.5 hidden text-xs text-muted sm:block">
        {description}
      </span>
    </div>
  );
}

function useConversion() {
  const [stepStatuses, setStepStatuses] = useState<StepStatus[]>([
    "idle",
    "idle",
    "idle",
  ]);
  const [result, setResult] = useState<"idle" | "success" | "error">("idle");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [errorDetail, setErrorDetail] = useState<string>("");
  const [errorHint, setErrorHint] = useState<string>("");
  const [pptxBlob, setPptxBlob] = useState<Blob | null>(null);
  const [pptxFileName, setPptxFileName] = useState<string>("result.pptx");

  const runConversion = useCallback(async (file: File) => {
    setResult("idle");
    setErrorMessage("");
    setErrorDetail("");
    setErrorHint("");
    setPptxBlob(null);
    setStepStatuses(["running", "idle", "idle"]);

    const delay = (ms: number) =>
      new Promise((resolve) => setTimeout(resolve, ms));

    try {
      await delay(400);
      setStepStatuses((s) => ["done", "running", "idle"]);
      await delay(400);
      setStepStatuses((s) => ["done", "done", "running"]);

      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("/api/convert", {
        method: "POST",
        body: formData,
      });

      await delay(300);
      setStepStatuses((s) => ["done", "done", "done"]);

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setErrorMessage(data.error ?? "変換に失敗しました");
        setErrorDetail(data.detail ?? "");
        setErrorHint(data.hint ?? "");
        setResult("error");
        return;
      }

      const blob = await res.blob();
      const disposition = res.headers.get("Content-Disposition");
      const nameMatch = disposition?.match(/filename\*?=(?:UTF-8'')?"?([^";\n]+)"?/i) ?? disposition?.match(/filename="?([^";\n]+)"?/i);
      const fileName = nameMatch ? decodeURIComponent(nameMatch[1].trim()) : file.name.replace(/\.pdf$/i, ".pptx");

      setPptxBlob(blob);
      setPptxFileName(fileName);
      setResult("success");
    } catch (e) {
      setStepStatuses((s) => {
        const next = [...s];
        const i = next.findIndex((x) => x === "running");
        if (i >= 0) next[i] = "error";
        return next;
      });
      setErrorMessage(e instanceof Error ? e.message : "変換中にエラーが発生しました");
      setErrorDetail("");
      setErrorHint("");
      setResult("error");
    }
  }, []);

  const downloadPptx = useCallback(() => {
    if (!pptxBlob) return;
    const url = URL.createObjectURL(pptxBlob);
    const a = document.createElement("a");
    a.href = url;
    a.download = pptxFileName;
    a.click();
    URL.revokeObjectURL(url);
  }, [pptxBlob, pptxFileName]);

  const reset = useCallback(() => {
    setStepStatuses(["idle", "idle", "idle"]);
    setResult("idle");
    setErrorMessage("");
    setErrorDetail("");
    setErrorHint("");
    setPptxBlob(null);
  }, []);

  return { stepStatuses, result, errorMessage, errorDetail, errorHint, pptxBlob, pptxFileName, runConversion, downloadPptx, reset };
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [optionsOpen, setOptionsOpen] = useState(false);
  const [useTemplate, setUseTemplate] = useState(false);
  const [useAiLayout, setUseAiLayout] = useState(true);

  const {
    stepStatuses,
    result,
    errorMessage,
    errorDetail,
    errorHint,
    pptxBlob,
    pptxFileName,
    runConversion,
    downloadPptx,
    reset,
  } = useConversion();

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files?.[0];
    if (f?.name.toLowerCase().endsWith(".pdf")) setFile(f);
  }, []);

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const onDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  }, []);

  const onFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f?.name.toLowerCase().endsWith(".pdf")) setFile(f);
  }, []);

  const startConversion = useCallback(() => {
    if (!file) return;
    runConversion(file);
  }, [file, runConversion]);

  const clearFile = useCallback(() => {
    setFile(null);
    reset();
  }, [reset]);

  const isConverting =
    stepStatuses.some((s) => s === "running") ||
    (result === "idle" && stepStatuses[0] !== "idle");

  return (
    <div className="flex min-h-screen flex-col bg-background font-sans">
      <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col px-6 py-14 sm:py-20">
        {/* Hero: 北欧らしい余白とやわらかいタイポ */}
        <header className="text-center">
          <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            NotebookLM Transformer
          </h1>
          <p className="mt-4 text-lg text-muted">
            構造解析と再構築で、スライドを編集可能なPowerPointに
          </p>
          <p className="mt-1.5 text-sm text-muted/90">
            構造抽出 → レイアウト解析 → PPTX構築
          </p>
        </header>

        {/* Upload: 角丸・ソフトな枠・ドロップ時はアクセント色 */}
        <section className="mt-12 w-full">
          <div
            onDrop={onDrop}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            className={`rounded-3xl border-2 border-dashed p-10 transition-all duration-200 ${
              dragOver
                ? "border-accent bg-accent-soft/30"
                : "border-border bg-surface"
            }`}
          >
            <input
              type="file"
              accept=".pdf"
              onChange={onFileChange}
              className="hidden"
              id="pdf-upload"
            />
            {file ? (
              <div className="flex flex-col items-center gap-4">
                <p className="text-sm font-medium text-foreground">
                  {file.name}
                </p>
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={startConversion}
                    disabled={isConverting}
                    className="rounded-xl bg-accent px-5 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-accent-hover disabled:opacity-50"
                  >
                    {isConverting ? "変換中…" : "変換を開始"}
                  </button>
                  <button
                    type="button"
                    onClick={clearFile}
                    disabled={isConverting}
                    className="rounded-xl border border-border bg-surface-soft px-5 py-2.5 text-sm font-medium text-foreground hover:bg-border/50 disabled:opacity-50"
                  >
                    解除
                  </button>
                </div>
              </div>
            ) : (
              <label
                htmlFor="pdf-upload"
                className="flex cursor-pointer flex-col items-center gap-3 text-muted hover:text-foreground"
              >
                <span className="text-5xl" aria-hidden>📄</span>
                <span className="text-sm font-medium">
                  PDFをドラッグ＆ドロップ、またはクリックして選択
                </span>
                <span className="text-xs">NotebookLMのスライドPDF（.pdf）</span>
              </label>
            )}
          </div>

          {/* Options: 折りたたみ・やわらかい背景 */}
          <div className="mt-5">
            <button
              type="button"
              onClick={() => setOptionsOpen((o) => !o)}
              className="text-sm text-muted hover:text-foreground"
            >
              {optionsOpen ? "オプションを閉じる" : "オプションを開く"}
            </button>
            {optionsOpen && (
              <div className="mt-3 rounded-2xl border border-border bg-surface-soft p-5">
                <label className="flex cursor-pointer items-center gap-3 text-sm text-foreground">
                  <input
                    type="checkbox"
                    checked={useTemplate}
                    onChange={(e) => setUseTemplate(e.target.checked)}
                    className="rounded border-border text-accent focus:ring-accent"
                  />
                  自社テンプレート（.potx）を使用
                </label>
                <label className="mt-3 flex cursor-pointer items-center gap-3 text-sm text-foreground">
                  <input
                    type="checkbox"
                    checked={useAiLayout}
                    onChange={(e) => setUseAiLayout(e.target.checked)}
                    className="rounded border-border text-accent focus:ring-accent"
                  />
                  AIでレイアウト解析（タイトル・箇条書きの区別）
                </label>
              </div>
            )}
          </div>
        </section>

        {/* Pipeline: ステップをやわらかいカード風に */}
        {(stepStatuses.some((s) => s !== "idle") || result !== "idle") && (
          <section className="mt-12 w-full">
            <h2 className="mb-4 text-sm font-medium text-muted">
              変換パイプライン
            </h2>
            <div className="flex items-start">
              {STEP_LABELS.map((step, i) => (
                <div key={i} className="flex flex-1 flex-col items-center">
                  <StepIndicator
                    stepIndex={i}
                    status={stepStatuses[i] ?? "idle"}
                    label={step.short}
                    description={step.desc}
                  />
                  {i < STEP_LABELS.length - 1 && (
                    <div
                      className="mt-6 w-8 shrink-0 self-center border-t-2 border-border"
                      aria-hidden
                    />
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Result: 成功は北欧グリーン・やさしいトーン */}
        {result === "success" && (
          <section className="mt-12 rounded-3xl border border-success/30 bg-success-soft p-6">
            <p className="font-medium text-success">
              変換が完了しました
            </p>
            <p className="mt-1 text-sm text-foreground/90">
              {pptxFileName}
            </p>
            <div className="mt-5 flex gap-3">
              <button
                type="button"
                onClick={downloadPptx}
                disabled={!pptxBlob}
                className="rounded-xl bg-success px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-success/90 disabled:opacity-50"
              >
                ダウンロード
              </button>
              <button
                type="button"
                onClick={clearFile}
                className="rounded-xl border border-success/50 bg-surface px-4 py-2.5 text-sm font-medium text-success hover:bg-success-soft"
              >
                もう1つ変換する
              </button>
            </div>
          </section>
        )}

        {result === "error" && (
          <section className="mt-12 rounded-3xl border border-error/30 bg-error-soft p-6">
            <p className="font-medium text-error">
              エラー
            </p>
            <p className="mt-1 text-sm text-foreground/90">
              {errorMessage}
            </p>
            {errorHint && (
              <p className="mt-2 text-sm font-medium text-foreground/90">
                {errorHint}
              </p>
            )}
            {errorDetail && (
              <pre className="mt-3 max-h-40 overflow-auto rounded-lg bg-black/10 p-3 text-xs text-foreground/80 whitespace-pre-wrap break-words">
                {errorDetail}
              </pre>
            )}
            <button
              type="button"
              onClick={() => file && runConversion(file)}
              className="mt-4 rounded-xl bg-error/90 px-4 py-2.5 text-sm font-medium text-white hover:bg-error"
            >
              再試行
            </button>
          </section>
        )}

        {/* CLI hint: 控えめなカード */}
        <section className="mt-12 w-full rounded-3xl border border-border bg-surface p-6 shadow-sm">
          <p className="text-sm font-medium text-foreground">
            今すぐ変換する（CLI）
          </p>
          <pre className="mt-3 overflow-x-auto rounded-xl bg-surface-soft px-4 py-3 text-sm text-muted">
            <code>
              {`python -m src.main input/slide.pdf -o output/result.pptx`}
            </code>
          </pre>
        </section>

        {/* Footer: 控えめで読みやすい */}
        <footer className="mt-14 text-center text-sm text-muted">
          <p>
            MVP: PyMuPDFでテキスト座標を抜き、python-pptxで同じ位置に配置
          </p>
          <p className="mt-1">
            PyMuPDF · python-pptx · OpenCV / Pillow · LLM (Claude)
          </p>
        </footer>
      </main>
    </div>
  );
}
