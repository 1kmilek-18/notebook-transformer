import { test, expect } from "@playwright/test";

test.describe("NotebookLM Transformer ホーム", () => {
  test("タイトルとヒーローが表示される", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "NotebookLM Transformer" })).toBeVisible();
    await expect(page.getByText("構造解析と再構築で、スライドを編集可能なPowerPointに")).toBeVisible();
    await expect(page.getByText("構造抽出 → レイアウト解析 → PPTX構築")).toBeVisible();
  });

  test("PDFアップロードエリアが表示される", async ({ page }) => {
    await page.goto("/");
    await expect(
      page.getByText("PDFをドラッグ＆ドロップ、またはクリックして選択")
    ).toBeVisible();
    await expect(page.getByText("NotebookLMのスライドPDF（.pdf）")).toBeVisible();
    await expect(page.getByRole("button", { name: "オプションを開く" })).toBeVisible();
  });

  test("オプションを開くとチェックボックスが表示される", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "オプションを開く" }).click();
    await expect(page.getByLabel("自社テンプレート（.potx）を使用")).toBeVisible();
    await expect(page.getByLabel("AIでレイアウト解析（タイトル・箇条書きの区別）")).toBeVisible();
    await page.getByRole("button", { name: "オプションを閉じる" }).click();
    await expect(page.getByRole("button", { name: "オプションを開く" })).toBeVisible();
  });

  test("ファイル選択後は「変換を開始」「解除」ボタンが表示される", async ({ page }) => {
    await page.goto("/");
    await page.locator('input[type="file"]').setInputFiles({
      name: "sample.pdf",
      mimeType: "application/pdf",
      buffer: Buffer.from("%PDF-1.4 minimal"),
    });
    await expect(page.getByRole("button", { name: "変換を開始" })).toBeVisible();
    await expect(page.getByRole("button", { name: "解除" })).toBeVisible();
    await expect(page.getByText("sample.pdf")).toBeVisible();
  });

  test("変換を開始するとパイプライン表示と完了メッセージが出る", async ({ page }) => {
    await page.goto("/");
    await page.locator('input[type="file"]').setInputFiles({
      name: "test.pdf",
      mimeType: "application/pdf",
      buffer: Buffer.from("%PDF-1.4"),
    });
    await page.getByRole("button", { name: "変換を開始" }).click();
    await expect(page.getByText("変換パイプライン")).toBeVisible({ timeout: 3000 });
    await expect(page.getByText("変換中…").or(page.getByRole("button", { name: "変換を開始" }))).toBeVisible();
    await expect(page.getByText("変換が完了しました")).toBeVisible({ timeout: 10000 });
    await expect(page.getByText("test.pptx")).toBeVisible();
  });

  test("解除でファイル選択をクリアできる", async ({ page }) => {
    await page.goto("/");
    await page.locator('input[type="file"]').setInputFiles({
      name: "dummy.pdf",
      mimeType: "application/pdf",
      buffer: Buffer.from("%PDF"),
    });
    await expect(page.getByText("dummy.pdf")).toBeVisible();
    await page.getByRole("button", { name: "解除" }).click();
    await expect(page.getByText("PDFをドラッグ＆ドロップ、またはクリックして選択")).toBeVisible();
    await expect(page.getByText("dummy.pdf")).not.toBeVisible();
  });

  test("CLI案内が表示される", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("今すぐ変換する（CLI）")).toBeVisible();
    await expect(page.getByText("python -m src.main input/slide.pdf -o output/result.pptx")).toBeVisible();
  });

  test("フッターが表示される", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText("PyMuPDF · python-pptx · OpenCV / Pillow · LLM (Claude)")).toBeVisible();
  });
});
