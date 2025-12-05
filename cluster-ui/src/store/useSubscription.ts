// import { create } from 'zustand'
// import { Subscriptions } from '../models/subscriptions'

// export interface  I_subscriptions_store{
//   subscriptions:Subscriptions[],
//   setSubscriptions:(newSubscriptions:Subscriptions[])=>void,
//   clearSubscriptions:()=>void
// }
// export const useSubscriptions = create<I_subscriptions_store>((set) => ({
//   subscriptions: [],
//   setSubscriptions: (newSubscriptions: Subscriptions[]) => set(() => ({ subscriptions: [...newSubscriptions] })),
//   clearSubscriptions: () => set({ subscriptions: [] })
// }))


// ? example to setup store from zustand - currently zustand is pruned
