import { spawnSync } from "child_process";
import { existsSync, mkdirSync } from "fs";
import { readFile, unlink, writeFile } from "fs/promises";
import path from "path";

export const dynamic = "force-dynamic";
export const maxDuration = 60;

const PROJECT_ROOT = path.resolve(process.cwd(), "..");
const TMP_DIR = path.join(PROJECT_ROOT, ".tmp", "convert");
const PYTHON_BIN = existsSync(path.join(PROJECT_ROOT, ".venv", "bin", "python"))
  ? path.join(PROJECT_ROOT, ".venv", "bin", "python")
  : "python3";

export async function POST(request: Request) {
  let inputPath: string | null = null;
  let outputPath: string | null = null;

  try {
    const formData = await request.formData();
    const file = formData.get("file") as File | null;
    if (!file || !file.name.toLowerCase().endsWith(".pdf")) {
      return new Response(
        JSON.stringify({ error: "PDFファイルを選択してください。" }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }

    if (!existsSync(TMP_DIR)) {
      mkdirSync(TMP_DIR, { recursive: true });
    }

    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    const base = path.join(TMP_DIR, `notebooklm-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`);
    inputPath = `${base}.pdf`;
    outputPath = `${base}.pptx`;

    await writeFile(inputPath, buffer);

    const { status, stderr, error } = spawnSync(
      PYTHON_BIN,
      ["-m", "src.main", inputPath, "-o", outputPath, "--no-save-images"],
      {
        cwd: PROJECT_ROOT,
        env: { ...process.env, PYTHONPATH: PROJECT_ROOT },
        encoding: "utf-8",
        timeout: 120000,
      }
    );

    if (error) {
      return new Response(
        JSON.stringify({
          error: "変換の実行に失敗しました。Python の環境を確認してください。",
          detail: error.message,
        }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }

    if (status !== 0) {
      const stderrStr = (stderr ?? "").trim();
      const detail = stderrStr.slice(0, 800) || "（Python の標準エラー出力はありません）";
      const isMissingModule = /ModuleNotFoundError|No module named ['"]/.test(stderrStr);
      const hint = isMissingModule
        ? "対処: プロジェクトルートで仮想環境を有効化し、pip install -r requirements.txt を実行してください。"
        : undefined;
      return new Response(
        JSON.stringify({
          error: isMissingModule ? "Python の依存パッケージが不足しています。" : "変換に失敗しました。",
          detail,
          hint,
        }),
        { status: 422, headers: { "Content-Type": "application/json" } }
      );
    }

    const outExists = existsSync(outputPath);
    if (!outExists) {
      return new Response(
        JSON.stringify({ error: "出力ファイルが生成されませんでした。" }),
        { status: 500, headers: { "Content-Type": "application/json" } }
      );
    }

    const pptxBuffer = await readFile(outputPath);
    const outFileName = file.name.replace(/\.pdf$/i, ".pptx");

    return new Response(pptxBuffer, {
      status: 200,
      headers: {
        "Content-Type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "Content-Disposition": `attachment; filename="${encodeURIComponent(outFileName)}"`,
      },
    });
  } finally {
    if (inputPath) {
      unlink(inputPath).catch(() => {});
    }
    if (outputPath) {
      unlink(outputPath).catch(() => {});
    }
  }
}
