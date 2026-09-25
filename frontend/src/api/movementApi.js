import api from "./axios";


const movementApi = {


    getAll: () =>
        api.get("/storage/movements"),



};


export default movementApi;