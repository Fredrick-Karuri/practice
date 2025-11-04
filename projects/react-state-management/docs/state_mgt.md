Stale closure happens when a function remembers old variables or state from when it was first created and doesnt see the updated values later

```javascript
function ChatRoom({roomId}){
const serverUrl = 'wss://chat.example.com'
const [messages,setMessages] = useState([]) 

 useEffect(() => {
     const ws = new WebSocket(`${serverUrl}/${roomId}`);
  
  ws.onmessage = (event) => {
      setMessages(prev => [...prev, event.data]);
  };

  return () => {
      ws.close(); // Cleanup function
  };
}, [roomId]); 
}
```
What happens if you:
A.Use [] (empty array)?
B.Use [roomId, messages]?
C.Omit it entirely (no array)?

The dependency array is critical as it tells react when to resynchronize the effect in our case tearing down an old connection and establishing a new one
Case A: the effect will run only once, when the component first mounts and never during  re-renders.So if we change to a different room , the ui might say room 2 but the data  will still be of room 1, the initial one.(room1 data, room2 UI)
Case B: adding messages would create an infinite loop . The ws.messages callback updates the messages state causing the component to rerender, because the messages are in the dependency array, this will cause the effect to run again, creating a new ws connection, then we'll send messages and the cycle will go on ...
case C: it will be same as empty dependency array but worse. when a message is received, the component will re-render, and since there is no dependency array, this re-render will trigger the effect again , hence a new connection for the same room, it will happen each time a message is received.(connection storm)

ESLint will yell at you to add serverUrl to the deps. Should you?

Three ways to fix the lint warning:

1.Move it outside: const serverUrl = "wss://..." above component (best - it's truly static)
2.Add to deps: [roomId, serverUrl] (safe but unnecessary re-runs if you change it)
3.Ignore the warning: (dangerous - teaches you to ignore the linter)

useReducer is handly when we need to do multiple related state updates in one atomic action.
Use it when:
1.one user action updates multiple state pieces
2.state updates depend on previous state in complex ways
3.you want to enforce valid state transitions(can't delete without recalculating)

useMemo caches values, useCallback caches functions

Q1: "When would you NOT use useEffect cleanup?"
if the effect does not create anything that needs to be explicitly stopped , cancelled or undone ie id effect is a one time operaiton that creates no subscriptions ,timers etc
Q2: "What's the difference between useEffect and useLayoutEffect?"
useEffect runs asynchronously after the browser has painted thus good for non visual effects like data fetching while useLayoutEffect runs synchronously , before the browser paints essential for visual updates
Q3: "Why shouldn't you call hooks inside conditional
react relies on a soncistent order of hook calls to correctly associate state with a specific hook during rerenders, conditionals break this and weird bugs emerge
```javascript
// First render:
const [name, setName] = useState('');     // Hook 0
const [age, setAge] = useState(0);        // Hook 1
const [email, setEmail] = useState('');   // Hook 2

// React's internal array:
[
  { state: '', setState: fn },  // index 0 → name
  { state: 0, setState: fn },   // index 1 → age  
  { state: '', setState: fn }   // index 2 → email
]
```
Follow-up: "So hooks must be called in the same order every render. How does React actually track which state belongs to which useState call?"
React uses an array (or linked list in Fiber architecture) indexed by call order.If you conditionally skip hook 1, the indexes shift and email gets mapped to age's state. Chaos. ie

In 2 sentences, explain when you'd use Context vs Redux/Zustand.
Use Context for infrequent updates with few consumers, like theme or authentication state. Choose Redux or Zustand when you have frequent updates affecting many components, since Context re-renders all consumers on every change while state management libraries use selectors to prevent unnecessary re-renders.

In 2 sentences explain what react.memo is:
It is a higher order component(HOC) in react that prevents a component from re-rendering if its props haven't changed . Its mainly used to optimize performance by memoizing functional components, avoiding unnecessary renders in large/complex UIs.
