import {expect,test} from '@playwright/test';

test('capture functional mission workspace',async({page},testInfo)=>{
  await page.goto('/mission?mission=1');
  await expect(page.getByText('MISSION CHECKLIST')).toBeVisible();
  await page.screenshot({path:`screenshots/${testInfo.project.name}-functional-mission-workspace.png`,fullPage:true});
});

test('capture opened analytics workspace',async({page},testInfo)=>{
  await page.goto('/analytics');
  await page.getByRole('button',{name:'Open Excel Workbench',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Excel Workbench workspace'})).toBeVisible();
  await page.screenshot({path:`screenshots/${testInfo.project.name}-functional-analytics-workspace.png`,fullPage:true});
});
