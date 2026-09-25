import { useEffect, useMemo, useState } from "react";

import {
  Plus,
  Pencil,
  Trash2,
  Warehouse,
  Search,
  MapPin,
  Boxes,
  CheckCircle,
  AlertTriangle,
  X
} from "lucide-react";

import api from "../api/axios";
import "../styles/Storage.css";

export default function Storage(){

const emptyPosition = () => ({
  zone_id:"",
  position_code:"",
  position_type:"STORAGE_SLOT",
  max_weight:0,
  x_coordinate:0,
  y_coordinate:0
});

const emptyZone = () => ({
  code:"",
  name:"",
  zone_type:"",
  capacity:0,
  latitude:"",
  longitude:""
});


const [zones,setZones]=useState([]);
const [positions,setPositions]=useState([]);

const [search,setSearch]=useState("");
const [statusFilter,setStatusFilter]=useState("ALL");
const [zoneFilter,setZoneFilter]=useState("ALL");

const [showZone,setShowZone]=useState(false);

const [editingZone,setEditingZone]=useState(null);

const [zoneForm,setZoneForm]=useState(emptyZone());


async function loadData(){
try{
const z=await api.get("/storage/zones");
const p=await api.get("/storage/positions");

setZones(z.data);
setPositions(p.data);

}catch(e){
console.log(e);
}
}


useEffect(()=>{
loadData();
},[]);


const filteredPositions=useMemo(()=>{

return positions.filter(p=>{

const searchText = [
p.position_code,
p.position_type,
p.zone_id,
p.zone?.name,
p.zone?.zone_type
]
.filter(Boolean)
.join(" ")
.toLowerCase();

const searchValue = search.trim().toLowerCase();

const searchOk =
searchValue === "" ||
searchText.includes(searchValue);

const statusOk =
statusFilter==="ALL" ||
(statusFilter==="FREE" && !p.occupied) ||
(statusFilter==="OCCUPIED" && p.occupied);

const zoneOk =
zoneFilter==="ALL" ||
String(p.zone_id)===String(zoneFilter);

return searchOk && statusOk && zoneOk;

});

},[positions,search,statusFilter,zoneFilter]);


async function saveZone(){

if(editingZone)
await api.put(`/storage/zones/${editingZone}`,zoneForm);
else
await api.post("/storage/zones/create",zoneForm);

setShowZone(false);
setEditingZone(null);
setZoneForm(emptyZone());
loadData();

}


async function remove(url){
if(confirm("Delete this item?")){
await api.delete(url);
loadData();
}
}


return (

<div className="storage-page">

<header className="storage-header">
<h1><Warehouse/> Storage Management</h1>
<p>Manage zones, positions and storage capacity</p>
</header>


<div className="storage-kpis">
<div><Warehouse/><label>Zones</label><strong>{zones.length}</strong></div>
<div><Boxes/><label>Positions</label><strong>{positions.length}</strong></div>
<div><AlertTriangle/><label>Occupied</label><strong>{positions.filter(x=>x.occupied).length}</strong></div>
<div><CheckCircle/><label>Available</label><strong>{positions.filter(x=>!x.occupied).length}</strong></div>
</div>


<section className="storage-panel">

<div className="section-title">
<h2>Storage Zones</h2>
<button onClick={()=>{setZoneForm(emptyZone());setShowZone(true)}}>
<Plus/> Add Zone
</button>
</div>


<div className="zone-grid">

{zones.map(z=>

<div className="zone-card" key={z.id}>

<h3>{z.name}</h3>
<p>{z.zone_type}</p>

<div className="capacity">
Capacity
<strong>{z.capacity}</strong>
</div>

<div className="actions">

<button onClick={()=>{
setEditingZone(z.id);
setZoneForm(z);
setShowZone(true);
}}>
<Pencil/>
</button>

<button onClick={()=>remove(`/storage/zones/${z.id}`)}>
<Trash2/>
</button>

</div>

</div>

)}

</div>
</section>


<section className="storage-panel">

<div className="section-title">
<h2>Storage Positions</h2>


</div>


<div className="filters">

<div>
<Search/>
<input
type="text"
placeholder="Search position..."
value={search}
autoComplete="off"
onChange={(e)=>{
setSearch(e.target.value);
}}
/>
</div>


<select value={statusFilter} onChange={e=>setStatusFilter(e.target.value)}>
<option value="ALL">All Status</option>
<option value="FREE">Free</option>
<option value="OCCUPIED">Occupied</option>
</select>


<select value={zoneFilter} onChange={e=>setZoneFilter(e.target.value)}>
<option value="ALL">All Zones</option>

{zones.map(z=>
<option key={z.id} value={z.id}>{z.name}</option>
)}

</select>

</div>


<div className="position-list">

{filteredPositions.map(p=>

<div className="position-card" key={p.id}>

<div>
<h3>{p.position_code}</h3>
<p><MapPin/> {p.position_type}</p>
</div>

<div>
Capacity
<strong>{p.max_weight} kg</strong>
</div>

<span className={p.occupied?"occupied":"free"}>
{p.occupied?"Occupied":"Free"}
</span>

<div className="actions">

<button onClick={()=>remove(`/storage/positions/${p.id}`)}>
<Trash2/>
</button>

</div>

</div>

)}

</div>

</section>


{showZone &&

<div className="storage-modal-bg">

<div className="storage-modal">

<X onClick={()=>{
setShowZone(false);
}}/>

<h2>Zone</h2>


{showZone && <>

<input placeholder="Zone code"
value={zoneForm.code}
onChange={e=>setZoneForm({...zoneForm,code:e.target.value})}
/>

<input placeholder="Zone name"
value={zoneForm.name}
onChange={e=>setZoneForm({...zoneForm,name:e.target.value})}
/>


<select value={zoneForm.zone_type}
onChange={e=>setZoneForm({...zoneForm,zone_type:e.target.value})}>

<option value="">Select Type</option>
<option value="VEHICLE_YARD">Vehicle Yard</option>
<option value="CONTAINER_YARD">Container Yard</option>
<option value="PACKAGE_AREA">Package Area</option>
<option value="BULK_SILO_AREA">Bulk Silo Area</option>

</select>


<input placeholder="Capacity"
type="number"
value={zoneForm.capacity}
onChange={e=>setZoneForm({...zoneForm,capacity:e.target.value})}
/>


<input
placeholder="Latitude"
type="number"
step="any"
value={zoneForm.latitude}
onChange={e=>
setZoneForm({
...zoneForm,
latitude:e.target.value
})
}
/>


<input
placeholder="Longitude"
type="number"
step="any"
value={zoneForm.longitude}
onChange={e=>
setZoneForm({
...zoneForm,
longitude:e.target.value
})
}
/>


<button onClick={saveZone}>Save Zone</button>

</>}


</div>
</div>

}


</div>

);

}
