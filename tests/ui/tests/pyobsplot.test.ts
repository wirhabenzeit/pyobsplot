import { expect, galata, test } from '@jupyterlab/galata';

import * as path from 'path';

async function test_notebook(page, notebook, renderer) {
    const notebook_file = `${notebook}.ipynb`;
    await page.notebook.openByPath(notebook_file);
    await page.notebook.activate(notebook_file);

    const captures = new Array<Buffer>();
    const cellCount = await page.notebook.getCellCount();

    if (renderer) {
        // Replace first cell by Obsplot + set_renderer
        await page.notebook.setCell(0, "code", `from pyobsplot import Obsplot, Plot, d3, Math, js; Obsplot.set_renderer('${renderer}'); print('${renderer}')`)
    }

    await page.notebook.runCellByCell({
        onAfterCellRun: async (cellIndex: number) => {
            const cell = await page.notebook.getCellOutput(cellIndex);
            if (cell) {
                captures.push(await cell.screenshot());
            }
        },
    });

    await page.notebook.save();

    for (let i = 0; i < (cellCount); i++) {
        const image = renderer ? `${renderer}-${notebook}-cell-${i}.png` : `${notebook}-cell-${i}.png`
        expect(captures[i]).toMatchSnapshot(image);
    }
}

test.describe('Visual Regression', () => {

    test.beforeEach(async ({ page, tmpPath }) => {
        await page.contents.uploadDirectory(
            path.resolve(path.resolve(''), `./tests/ui/tests/notebooks/`),
            '/'
        );
        await page.filebrowser.openDirectory('/');
    });

    // notebooks to test with each renderer
    let notebooks = ["syntax", "dates", "errors", "complex_plots", "data_sources", "transforms", "geo"];
    for (let renderer of ["widget", "jsdom"]) {
        // check all notebooks
        for (let notebook of notebooks) {
            test(`${renderer} / ${notebook}.ipynb`, async ({ page }) => {
                await test_notebook(page, notebook, renderer);
            });
        }
    }

    // notebooks mixing renderers
    let mix_notebooks = ["mix_renderers"]
    for (let notebook of mix_notebooks) {
        test(`Mix / ${notebook}.ipynb`, async ({ page }) => {
            await test_notebook(page, notebook, null);
        });
    }

});

