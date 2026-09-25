import api from "./axios";


const operationApi = {


    movements(){

        return api.get(
            "/storage/movements"
        );

    },


    occupancy(){

        return api.get(
            "/storage/occupancy"
        );

    }


};


export default operationApi;