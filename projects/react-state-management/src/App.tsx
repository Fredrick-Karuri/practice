
import "./App.css";
import { ChatRoom } from "./components/ChatRoom";
import { UserDataTable } from "./components/Users/UserDataTable";


function App() {
  return (
    <>
      <div>
        <h1>Chat Room</h1>
        <ChatRoom roomId="general" />
        <UserDataTable />
      </div>
    </>
  );
}

export default App;
