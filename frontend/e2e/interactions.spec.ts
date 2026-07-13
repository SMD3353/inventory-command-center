import {expect,test} from '@playwright/test';

test('active learning-map node opens its mission workspace',async({page})=>{
  await page.goto('/map');
  await page.getByRole('button',{name:/Receiving Dock/i}).click();
  await expect(page).toHaveURL(/\/mission\?mission=1$/);
  await expect(page.getByRole('heading',{name:'MISSION WORKSPACE'})).toBeVisible();
  await expect(page.locator('.mission-list button').first()).toHaveClass(/selected/);
});

test('locked learning-map nodes are disabled rather than misleading clicks',async({page})=>{
  await page.goto('/map');
  await expect(page.getByRole('button',{name:/Data Bay/i})).toBeDisabled();
  await expect(page.getByRole('button',{name:/Control Tower/i})).toBeDisabled();
});

test('analytics modules open an actionable workspace and route to a mission',async({page})=>{
  await page.goto('/analytics');
  await page.getByRole('button',{name:/OPEN EXCEL WORKBENCH/i}).click();
  await expect(page.getByRole('heading',{name:'Excel Workbench workspace'})).toBeVisible();
  await expect(page.getByText(/Your task/i)).toBeVisible();
  await page.getByRole('link',{name:/START RELATED MISSION/i}).click();
  await expect(page).toHaveURL(/\/mission\?mission=3$/);
});

test('portfolio case file can be opened and closed',async({page})=>{
  await page.goto('/portfolio');
  const toggle=page.getByRole('button',{name:/VIEW CASE FILE/i});
  await toggle.click();
  await expect(page.getByText('Case evidence checklist')).toBeVisible();
  const close=page.getByRole('button',{name:/CLOSE CASE FILE/i});
  await expect(close).toBeVisible();
  await close.click();
  await expect(page.getByText('Case evidence checklist')).toBeHidden();
});

test('all primary navigation links reach their destination',async({page},testInfo)=>{
  const routes=[
    ['Command Center','/'],['Learning Map','/map'],['Mission Workspace','/mission'],
    ['Simulation Room','/simulation'],['Analytics Lab','/analytics'],
    ['Competency Matrix','/competencies'],['Portfolio Vault','/portfolio'],
    ['Rewards Center','/rewards'],["Manager's Office",'/manager'],
  ] as const;
  await page.goto('/');
  for(const [label,path] of routes){
    if(testInfo.project.name==='mobile')await page.getByRole('button',{name:'Open navigation'}).click();
    await page.getByRole('link',{name:label,exact:true}).click();
    await expect(page).toHaveURL(new RegExp(`${path==='/'?'/$':`${path}$`}`));
  }
});

test('command-center mission call to action opens Mission Workspace',async({page})=>{
  await page.goto('/');
  await page.getByRole('link',{name:/BEGIN INVESTIGATION/i}).click();
  await expect(page.getByRole('heading',{name:'MISSION WORKSPACE'})).toBeVisible();
});

test('mission evidence cannot be submitted with an empty reflection',async({page})=>{
  await page.goto('/mission?mission=1');
  await page.getByRole('button',{name:/SUBMIT EVIDENCE|RESUBMIT EVIDENCE/}).click();
  await expect(page.getByRole('alert')).toContainText('at least 20 characters');
});

test('every analytics module opens its matching actionable workspace',async({page},testInfo)=>{
  await page.goto('/analytics');
  for(const title of ['SQL Query Bay','Excel Workbench','Dashboard Studio']){
    await page.getByRole('button',{name:`Open ${title}`,exact:true}).click();
    const workspace=page.getByRole('heading',{name:`${title} workspace`});
    await expect(workspace).toBeVisible();
    if(testInfo.project.name==='mobile')expect((await workspace.boundingBox())?.y).toBeLessThan(220);
    await expect(page.getByText('Your task',{exact:true})).toBeVisible();
  }
});

test('each management decision logs the selected action',async({page})=>{
  await page.goto('/manager');
  for(const action of ['Reallocate stock','Expedite open PO','Offer substitute','Escalate revenue risk']){
    await page.getByRole('button',{name:new RegExp(action)}).click();
    await expect(page.getByText(`Decision logged: ${action}`)).toBeVisible();
  }
});

test('an unlocked reward can be activated and reports saved status',async({page,request})=>{
  const dashboard=await (await request.get('/api/dashboard')).json();
  dashboard.rewards[0]={...dashboard.rewards[0],unlocked:true,claimed:false};
  await page.route('**/api/dashboard',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(dashboard)}));
  await page.route('**/api/rewards/1/claim',async route=>{
    dashboard.rewards[0].claimed=true;
    await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({reward:dashboard.rewards[0]})});
  });
  await page.goto('/rewards');
  await page.getByRole('button',{name:'ACTIVATE',exact:true}).first().click();
  await expect(page.getByRole('status')).toContainText('activated and saved');
  await expect(page.getByRole('button',{name:'ACTIVATED',exact:true}).first()).toBeDisabled();
});

test('dataset download endpoint returns a CSV file',async({request})=>{
  const response=await request.get('/datasets/regional_inventory.csv');
  expect(response.ok()).toBeTruthy();
  expect(response.headers()['content-type']).toContain('text/csv');
  expect((await response.text()).split('\n').length).toBeGreaterThan(200);
});
