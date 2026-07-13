// @vitest-environment jsdom
import {fireEvent,render,screen} from '@testing-library/react'
import '@testing-library/jest-dom/vitest'
import {MemoryRouter} from 'react-router-dom'
import {beforeEach,expect,test,vi} from 'vitest'
import App from './App'

const mocks=vi.hoisted(()=>({getDashboard:vi.fn()}))
const dashboard={
  profile:{name:'Mani',role:'Inventory Trainee',xp:0,level:1,streak:0,readiness:18,weekly_completed:0},
  missions:[{id:1,day:'01',title:'Map the inventory flow',type:'Foundation',duration:50,xp:80,status:'available',brief:'Trace flow',deliverable:'Worksheet',concepts:['SKU']}],
  competencies:[{name:'Inventory operations',level:1,score:34,target:80,accent:'cyan'}],
  rewards:[],portfolio:[],manager_cases:[],learning_map:[],alerts:[],kpis:[]
}

vi.mock('./lib/api',()=>({
  getDashboard:mocks.getDashboard,
  completeMission:async()=>({}),
  simulate:async()=>({safety_stock:39,reorder_point:333,order_up_to:375,risk:'controlled'}),
  claimReward:async()=>({})
}))

beforeEach(()=>{mocks.getDashboard.mockReset();mocks.getDashboard.mockResolvedValue(dashboard)})

test('renders command center and complete navigation',async()=>{
  render(<MemoryRouter><App/></MemoryRouter>)
  expect(await screen.findByRole('heading',{name:'COMMAND CENTER'})).toBeInTheDocument()
  for(const label of ['Learning Map','Mission Workspace','Simulation Room','Analytics Lab','Competency Matrix','Portfolio Vault','Rewards Center',"Manager's Office"]){
    expect(screen.getByText(label)).toBeInTheDocument()
  }
})

test('Reconnect recovers after an initial dashboard failure',async()=>{
  mocks.getDashboard.mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce(dashboard)
  render(<MemoryRouter><App/></MemoryRouter>)
  const reconnect=await screen.findByRole('button',{name:'Reconnect'})
  fireEvent.click(reconnect)
  expect(await screen.findByRole('heading',{name:'COMMAND CENTER'})).toBeInTheDocument()
  expect(screen.queryByText('Control tower offline')).not.toBeInTheDocument()
})
