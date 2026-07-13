export const API = import.meta.env.VITE_API_URL || '/api'
export async function getDashboard(){const r=await fetch(`${API}/dashboard`);if(!r.ok)throw new Error('Control tower offline');return r.json()}
export async function completeMission(id:number, score:number, reflection:string){const r=await fetch(`${API}/missions/${id}/complete`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({score,reflection})});if(!r.ok)throw new Error('Submission failed');return r.json()}
export async function simulate(input:Record<string,number>){const r=await fetch(`${API}/simulate`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(input)});if(!r.ok)throw new Error('Simulation failed');return r.json()}
export async function claimReward(id:number){const r=await fetch(`${API}/rewards/${id}/claim`,{method:'POST'});if(!r.ok)throw new Error(r.status===409?'Complete the reward requirement first':'Reward activation failed');return r.json()}
