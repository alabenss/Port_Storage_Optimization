import api from "./axios";


const storageApi = {


    getPositions: () =>
        api.get("/storage/positions"),



    getZones: () =>
        api.get("/storage/zones"),



    getOccupancy: () =>
        api.get("/storage/occupancy"),



    allocateManual: (data) =>
        api.post("/storage/manual-allocation", data),



    relocate: (cargoId) =>
        api.post(`/storage/relocate/cargo/${cargoId}`),



};


export default storageApi;