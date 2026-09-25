import {
    useEffect,
    useState
} from "react";

import {
    Activity,
    ArrowRight,
    Clock,
    Package,
    Move,
    RefreshCw
} from "lucide-react";

import operationApi from "../api/operationApi";


export default function Operations(){

    const [movements,setMovements] = useState([]);
    const [occupancy,setOccupancy] = useState(null);
    const [loading,setLoading] = useState(true);
    const [lastUpdate,setLastUpdate] = useState(null);


    async function load(){

        try{

            setLoading(true);

            const [m,o] = await Promise.all([
                operationApi.movements(),
                operationApi.occupancy()
            ]);

            setMovements(m.data || []);
            setOccupancy(o.data || null);
            setLastUpdate(new Date());

        }
        catch(error){

            console.log(error);

        }
        finally{

            setLoading(false);

        }

    }


    useEffect(()=>{

        load();

        const timer = setInterval(load,30000);

        return ()=>clearInterval(timer);

    },[]);


    if(loading && !lastUpdate){

        return (
            <div className="loading">
                Loading Operations Center...
            </div>
        );

    }


    return (

        <div>

            <div className="page-header">

                <h1 className="flex gap-3 items-center">
                    <Activity className="text-cyan-400"/>
                    Operations Center
                </h1>

                <p>
                    Real time terminal activity monitoring
                </p>

            </div>


            <button
                className="primary-button mb-6 flex gap-2 items-center"
                onClick={load}
            >
                <RefreshCw size={18}/>
                Refresh
            </button>


            <div className="kpi-grid">

                <div className="metric-card">
                    <Activity className="text-cyan-400"/>
                    <h3>Total Movements</h3>
                    <strong>{movements.length}</strong>
                </div>


                <div className="metric-card">
                    <Package className="text-green-400"/>
                    <h3>Occupied Positions</h3>
                    <strong>{occupancy?.occupied || 0}</strong>
                </div>


                <div className="metric-card">
                    <Move className="text-blue-400"/>
                    <h3>Availability</h3>
                    <strong>{occupancy?.available || 0}</strong>
                </div>


                <div className="metric-card">
                    <Clock className="text-cyan-400"/>
                    <h3>Last Update</h3>
                    <strong>
                        {lastUpdate ? lastUpdate.toLocaleTimeString() : "-"}
                    </strong>
                </div>

            </div>



            <div className="panel">

                <h2>
                    Activity Timeline
                </h2>


                <div>

                {
                    movements.length === 0
                    ?
                    <div className="empty-ai">
                        No movements found
                    </div>
                    :
                    movements.map((m)=>(

                        <div
                            key={m.id}
                            className="ai-row"
                        >

                            <Clock size={18}/>

                            <div>

                                <div>
                                    {new Date(m.created_at).toLocaleString()}
                                </div>

                                <strong>
                                    {m.action}
                                </strong>

                                <p>
                                    Cargo ID: {m.cargo_id}
                                </p>

                            </div>


                            <div style={{marginLeft:"auto"}} className="flex gap-3 items-center">

                                <span>
                                    {m.from_position || "ENTRY"}
                                </span>

                                <ArrowRight size={18}/>

                                <span>
                                    {m.to_position || "EXIT"}
                                </span>

                            </div>

                        </div>

                    ))
                }

                </div>

            </div>

        </div>

    );

}
