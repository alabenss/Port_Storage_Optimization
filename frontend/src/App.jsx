import {
  Routes,
  Route
} from "react-router-dom";


import Sidebar from "./components/Sidebar";


import Dashboard from "./pages/Dashboard";
import Cargo from "./pages/Cargo";
import Storage from "./pages/Storage";
import Operations from "./pages/Operations";
import ImportManifest from "./pages/Import";
import YardMap from "./pages/YardMap";
import AI from "./pages/AI";
import ManualAllocation from "./pages/ManualAllocation";
import Prediction from "./pages/Prediction";
import Reports from "./pages/Reports";
import Login from "./pages/Login";



function App() {


return (

<Routes>


{/* LOGIN */}

<Route

path="/login"

element={<Login />}

/>




{/* MAIN APPLICATION */}

<Route

path="/*"

element={


<div className="app-layout">


<Sidebar />



<main className="main-content">


<Routes>


<Route

path="/"

element={<Dashboard />}

/>



<Route

path="/cargo"

element={<Cargo />}

/>



<Route

path="/storage"

element={<Storage />}

/>



<Route

path="/operations"

element={<Operations />}

/>



<Route

path="/import"

element={<ImportManifest />}

/>



<Route

path="/map"

element={<YardMap />}

/>



<Route

path="/ai"

element={<AI />}

/>



<Route

path="/allocation"

element={<ManualAllocation />}

/>



<Route
 path="/prediction"
 element={<Prediction />}
/>



<Route

path="/reports"

element={<Reports />}

/>



</Routes>



</main>


</div>


}


/>



</Routes>


);


}


export default App;