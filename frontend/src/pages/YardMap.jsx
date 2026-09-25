import {
    MapContainer,
    TileLayer,
    Popup,
    Marker,
    LayersControl,
    ZoomControl,
    useMap
} from "react-leaflet";


import {
    useEffect,
    useState
} from "react";


import {
    Search,
    MapPin
} from "lucide-react";




import "../styles/YardMap.css";

import api from "../api/axios";

function FlyToLocation({ position }) {

    const map = useMap();


    useEffect(() => {

        if (position) {

            map.flyTo(
                position,
                18,
                {
                    duration: 1.5
                }
            );

        }

    }, [position, map]);


    return null;

}





export default function YardMap() {


    const [search, setSearch] = useState("");

    const [selected, setSelected] = useState(null);

    const [selectedInfo, setSelectedInfo] = useState(null);
    



    // ================================
    // SEARCH ZONES + REAL POSITIONS
    // ================================


    async function searchCargo(){


        const value = search
            .trim()
            .toLowerCase();



        if(!value){

            alert("Enter position code");

            return;

        }



        try {


            const response = await fetch(
                "http://127.0.0.1:8000/storage/positions"
            );


            const allPositions = await response.json();



            const found = allPositions.find(p =>

                p.position_code
                    ?.toLowerCase()
                    .includes(value)

            );



            if(found){


                if(
                    found.latitude &&
                    found.longitude
                ){


                    setSelected(
                        [
                            found.latitude,
                            found.longitude
                        ]
                    );


                    setSelectedInfo({

                        title: found.position_code,

                        zone: found.zone_id,

                        type: found.position_type,

                        status:

                            found.occupied

                                ? "Occupied"

                                : "Available"

                    });


                }

                else{


                    alert(
                        "Position has no GPS coordinates"
                    );


                }


                return;


            }



            alert(
                "Position not found"
            );


        }
        catch(error){

            console.log(
                "Search failed",
                error
            );

        }


    }






    // ================================
    // MAP DISPLAY
    // ================================


    return (


        <div className="yard-page">



            <div className="yard-header">



                <div>


                    <h1>


                        <MapPin size={28}/>


                        Digital Yard Map


                    </h1>



                    <p>

                        Live Djen Djen port navigation system

                    </p>



                </div>






                <div className="yard-search">



                    <input



                        placeholder="Search position / container..."



                        value={search}



                        onChange={e => setSearch(e.target.value)}



                    />





                    <button

                        onClick={searchCargo}

                    >



                        <Search size={18}/>



                        Find



                    </button>



                </div>



            </div>









            <div className="map-container">



                <MapContainer



                    center={[

                        36.8235,

                        5.8860

                    ]}



                    zoom={17}



                    className="leaflet-map"



                >





                    <LayersControl position="topright">



                        <LayersControl.BaseLayer

                            checked

                            name="Street Map"

                        >



                            <TileLayer

                                url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"

                            />



                        </LayersControl.BaseLayer>







                        <LayersControl.BaseLayer

                            name="Satellite"

                        >



                            <TileLayer


                                url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"


                            />



                        </LayersControl.BaseLayer>



                    </LayersControl>







                    <ZoomControl position="topleft"/>









                    {/* SEARCH RESULT ONLY */}


                    {
                    selected &&

                    <>

                    <FlyToLocation

                    key={selected.join(",")}

                    position={selected}

                    />


                    <Marker

                    position={selected}

                    >

                    <Popup>

                    <h3>

                    {
                    selectedInfo?.title
                    ||
                    "Location Found"
                    }

                    </h3>


                    <p>

                    Type:

                    {
                    selectedInfo?.type
                    }

                    </p>


                    <p>

                    Status:

                    {
                    selectedInfo?.status
                    }

                    </p>


                    </Popup>


                    </Marker>


                    </>

                    }


</MapContainer>



            </div>



        </div>


    );


}