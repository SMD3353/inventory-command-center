// @vitest-environment jsdom
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import { MemoryRouter } from 'react-router-dom'
import { test, expect, vi } from 'vitest'
import App from './App'

vi.mock('./lib/api', () => ({
  getDashboard: async () => ({
    profile:{name:'Mani',role:'Inventory Trainee',xp:0,level:1,streak:0,readiness:18,weekly_completed:0},
    missions:[{id:1,day:'01',title:'Map the inventory flow',type:'Foundation',duration:50,xp:80,status:'available',brief:'Trace flow',deliverable:'Worksheet',concepts:['SKU']}],
    competencies:[{name:'Inventory operations',level:1,score:34,target:80,accent:'cyan'}], rewards:[],portfolio:[],manager_cases:[],learning_map:[],alerts:[],kpis:[]
  }), completeMission: async()=>({}), simulate: async()=>({safety_stock:39,reorder_point:333,order_up_to:375,risk:'controlled'})
}))

test('renders command center and complete navigation', async () => {
  render(<MemoryRouter><App /></MemoryRouter>)
  expect(await screen.findByRole('heading', {name:'COMMAND CENTER'})).toBeInTheDocument()
  for (const label of ['Learning Map','Mission Workspace','Simulation Room','Analytics Lab','Competency Matrix','Portfolio Vault','Rewards Center',"Manager's Office"]) {
    expect(screen.getByText(label)).toBeInTheDocument()
  }
})
