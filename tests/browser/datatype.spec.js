const { test, expect } = require('@playwright/test');

test.beforeEach(async ({ page }) => {
  await page.goto('/tests/browser/fixture.html');
  await expect(page.locator('html')).toHaveAttribute('data-fonts', 'ready');
});

test('loads the Datatype variable font', async ({ page }) => {
  const fontLoaded = await page.evaluate(
    () => document.fonts.check('80px "Datatype"')
  );

  expect(fontLoaded).toBe(true);
  await expect(page.locator('#bar')).toHaveCSS('font-family', /Datatype/);
});

for (const chart of ['bar', 'spark', 'pie']) {
  test(`${chart} syntax is substituted by OpenType features`, async ({ page }) => {
    const renderedWidth = await page.locator(`#${chart}`).evaluate(
      element => element.getBoundingClientRect().width
    );
    const literalWidth = await page.locator(`#${chart}-raw`).evaluate(
      element => element.getBoundingClientRect().width
    );

    expect(renderedWidth).toBeGreaterThan(0);
    expect(renderedWidth).toBeLessThan(literalWidth * 0.75);
  });
}

test('width axis changes chart spacing', async ({ page }) => {
  const narrowWidth = await page.locator('#bar-narrow').evaluate(
    element => element.getBoundingClientRect().width
  );
  const wideWidth = await page.locator('#bar-wide').evaluate(
    element => element.getBoundingClientRect().width
  );

  expect(wideWidth).toBeGreaterThan(narrowWidth * 2);
});

test('weight axis visibly changes chart rendering', async ({ page }) => {
  const thin = await page.locator('#bar-thin').screenshot();
  const black = await page.locator('#bar-black').screenshot();

  expect(thin.equals(black)).toBe(false);
});

test('different pie values visibly produce different glyphs', async ({ page }) => {
  const quarter = await page.locator('#pie-25').screenshot();
  const threeQuarters = await page.locator('#pie-75').screenshot();

  expect(quarter.equals(threeQuarters)).toBe(false);
});
