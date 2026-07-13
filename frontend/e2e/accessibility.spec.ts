import {test,expect} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const screens=['/','/map','/mission','/simulation','/analytics','/competencies','/portfolio','/rewards','/manager'];

for(const path of screens){
  test(`no serious accessibility violations: ${path}`,async({page})=>{
    await page.goto(path);
    const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();
    const blocking=results.violations.filter(v=>v.impact==='critical'||v.impact==='serious');
    expect(blocking,blocking.map(v=>`${v.id}: ${v.description}`).join('\n')).toEqual([]);
  });
}
