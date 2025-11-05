import "./App.css";
import { ChatRoom } from "./components/ChatRoom";
import { ErrorBoundary } from "./components/Users/components/ErrorBoundary";
import { UserDashboard } from "./components/Users/UserDashboard";
import { UserDataTable } from "./components/Users/UserDataTable";

function App() {
  return (
    <>
      <div>
        <h1>Chat Room</h1>
        {/* <ChatRoom roomId="general" /> */}
        {/* <UserDataTable /> */}
        <ErrorBoundary>
          <UserDashboard />
        </ErrorBoundary>
      </div>
    </>
  );
}

export default App;
