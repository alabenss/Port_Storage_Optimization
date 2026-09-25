import api from "./axios";


const dashboardApi = {


    summary(){

        return api.get(
            "/dashboard/summary"
        );

    },


    zones(){

        return api.get(
            "/dashboard/zones"
        );

    },


    movements(){

        return api.get(
            "/dashboard/movements"
        );

    },


    ai(){

        return api.get(
            "/ai/dashboard"
        );

    }


};


export default dashboardApi;