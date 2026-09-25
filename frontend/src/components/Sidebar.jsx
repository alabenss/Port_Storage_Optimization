import { NavLink } from "react-router-dom";

import {
  LayoutDashboard,
  Package,
  Warehouse,
  Activity,
  Upload,
  Map,
  Brain,
  Anchor,
  ClipboardCheck,
  LogOut,
  FileText,
} from "lucide-react";



function Sidebar() {


  const links = [


    {
      path: "/",
      name: "Dashboard",
      icon: LayoutDashboard,
    },


    {
      path: "/cargo",
      name: "Cargo Management",
      icon: Package,
    },


    {
      path: "/storage",
      name: "Storage",
      icon: Warehouse,
    },


    {
      path: "/map",
      name: "Digital Yard",
      icon: Map,
    },


    {
      path: "/ai",
      name: "AI Control Center",
      icon: Brain,
    },


    {
      path: "/operations",
      name: "Operations",
      icon: Activity,
    },


    {
      path: "/import",
      name: "Import Manifest",
      icon: Upload,
    },


    {
      path: "/allocation",
      name: "Manual Allocation",
      icon: ClipboardCheck,
    },


    {
    path: "/prediction",
    name: "AI Prediction Center",
    icon: Brain,
    },


    {
      path: "/reports",
      name: "Reports",
      icon: FileText,
    },


  ];




  return (


    <aside className="sidebar">



      <div className="sidebar-logo">


        <div className="logo-icon">

          <Anchor size={25}/>

        </div>




        <div>

          <h2>
            DJENDJEN PORT
          </h2>




        </div>


      </div>







      <nav className="sidebar-nav">


        {
          links.map((item)=>{


            const Icon = item.icon;



            return (


              <NavLink


                key={item.path}


                to={item.path}


                end={item.path === "/"}



                className={({isActive}) =>

                  isActive

                  ?

                  "nav-item active"

                  :

                  "nav-item"

                }


              >



                <Icon size={20}/>



                <span>

                  {item.name}

                </span>



              </NavLink>


            );


          })
        }



      </nav>








      <button


        className="nav-item"


        onClick={() =>
          alert(
            "Logout system will be activated with authentication module"
          )
        }


      >


        <LogOut size={20}/>


        <span>

          Logout

        </span>


      </button>










    </aside>


  );


}



export default Sidebar;