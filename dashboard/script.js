const clockContainer = document.querySelector("#clock")
const dateContainer = document.querySelector("#date")
const updateClock = () => {
    clockContainer.innerHTML = new Date().toLocaleTimeString()
    dateContainer.innerHTML = new Date().toLocaleDateString()
}
updateClock()
setInterval(()=>{
    updateClock()
},1000)

const cpuLoad = document.querySelector("#cpuLoad")
const ramLoad = document.querySelector("#ramLoad")
const wifi = document.querySelector("#wifi")
const wifi_details = document.querySelector("#wifi_details")
const updateLoad = () => {
    fetch("/api/system").then(e=>e.json()).then(data=>{
        cpuLoad.innerHTML = `${data.cpu.toFixed(1)}%`
        ramLoad.innerHTML = `${data.ram.toFixed(1)}%`
        wifi_details.innerHTML = `<ul id="wifi_details">
                                    <li>SSID: ${data.wifi.ssid}</li>
                                    <li>Access Point: ${data.wifi.access_point}</li>
                                    <li>Bit Rate: ${data.wifi.bit_rate}</li>
                                    <li>Frequency: ${data.wifi.frequency}</li>
                                    <li>Link Quality: ${data.wifi.link_quality}</li>
                                    <li>Nickname: ${data.wifi.nickname}</li>
                                    <li>Noise Level: ${data.wifi.noise_level}</li>
                                    <li>Signal Level: ${data.wifi.signal_level}</li>
                                </ul>`
        fetch("/power_mode").then(e=>e.json()).then(data=>{
            document.getElementById("power_details").innerHTML = data.map(e=>`<li class="${e.active?"active":""}">
                <a target="_blank" href="/power_mode/${e.id}">${e.name.replace("MODE_","").replace("_"," ")}</a>
            </li>`).join("")
            setTimeout(()=>{
                updateLoad()
            },10*1000)
        })
    })
}
updateLoad()



document.querySelector("body").classList.add(window.innerWidth > window.innerHeight ? "normal" : "phone")
const x = document.getElementById("stream");

const webSocket = new WebSocket("ws://" + window.location.host.split(":")[0] + ":8081");
webSocket.onopen = (event) => {
    // webSocket.send("Here's some text that the server is urgently awaiting!");
};
webSocket.onmessage = (event) => {
    let img = event.data.substr(11)
    img = img.substr(0,img.length-1)
    console.log("new img")
    const image = `data:image/jpeg;base64,${img}`
    x.src = image;
}

const showLines = false

const traces = {
    blue: {
        x: [],
        y: [],
        mode: showLines?'lines+markers':'markers',
        type: 'scatter',
        marker: {
            color: 'rgb(0,0,255)',
        },
        line: {
            color: 'rgba(0,0,255,.2)',
        }
    },
    red: {
        x: [],
        y: [],
        type: 'scatter',
        mode: showLines?'lines+markers':'markers',
        marker: {
            color: 'rgb(255,0,0)',
        },
        line: {
            color: 'rgba(255,0,0,.2)',
        }
    },
    yellow: {
        x: [],
        y: [],
        type: 'scatter',
        mode: showLines?'lines+markers':'markers',
        marker: {
            color: 'rgb(255,255,0)',
        },
        line: {
            color: 'rgba(255,255,0,.2)',
        }
    },
    green: {
        x: [],
        y: [],
        type: 'scatter',
        mode: showLines?'lines+markers':'markers',
        marker: {
            color: 'rgb(0,255,0)',
        },
        line: {
            color: 'rgba(0,255,0,.2)',
        }
    },
    pink: {
        x: [],
        y: [],
        type: 'scatter',
        mode: showLines?'lines+markers':'markers',
        marker: {
            color: 'rgb(255,0,255)',
        },
        line: {
            color: 'rgba(255,0,255,.2)',
        }
    },
    black: {
        x: [],
        y: [],
        type: 'scatter',
        mode: 'markers',
        marker: {
            color: 'rgb(0,0,0)',
            size: [10,5],
        }
    },
    selected: {
        x: [],
        y: [],
        // yaxis: 'y2',
        mode: 'markers',
        type: 'scatter',
        marker: {
            color: 'rgb(0,0,0)',
            size: [10],
        }
    },
}

let rawTraces = null

let range = [0,0]

const plot = () => {
    // console.log(traces)
    const x = [
        ...traces.blue.x,
        ...traces.blue.y,
        ...traces.red.x,
        ...traces.red.y,
        ...traces.yellow.x,
        ...traces.yellow.y,
        ...traces.green.x,
        ...traces.green.y,
        ...traces.pink.x,
        ...traces.pink.y,
        ...traces.black.x,
        ...traces.black.y,
        ...traces.selected.x,
        ...traces.selected.y,
    ].sort((a,b)=>a-b)
    const tempRange = [x[0]-10, x[x.length-1]+10]
    if(tempRange[0]<range[0]) range[0] = tempRange[0]
    if(tempRange[1]>range[1]) range[1] = tempRange[1]
    // console.log(range)
    // Plotly.newPlot('myDiv', Object.values(traces), {
        
    const axis = {
        autorange: false,
        zerolinewidth: 0,
        zeroline: false,
        range,
    }
    Plotly.newPlot('myDiv', Object.values(traces), {
        width: 500,
        height: 500,
        autoscale: false,
        showlegend: false,
        yaxis: axis,
        xaxis: axis
    });
}
const img = new Image()

img.onload = function() {
    x.src = img.src;
};

// setInterval(()=>{
//     // img.src = `/image?t=${new Date().getTime()}`
//     x.src = `/image?t=${new Date().getTime()}`
// },1000)

const fillPlot = (tempData) => {
    console.log(tempData)
    const driveRoute = {
        x: [tempData.route.x,...tempData.route.next.map(e=>e.x)],
        y: [tempData.route.y,...tempData.route.next.map(e=>e.y)],
        mode: 'lines+markers', // lines+
        type: 'scatter',
        name: "Direct Path",
        active: false,
        line: {
            color: "rgba(255,255,255,.1)",
            width: 1
        },
        marker: {
            color: "#fff",
        },
    }
    
    const interpolatedDriveRoute = {
        x: tempData.curve.x,
        y: tempData.curve.y,
        mode: 'lines+markers',
        type: 'scatter',
        name: "Calculated Path",
        line: {
            color: "#fff"
        },
        marker: {
            color: "transparent"
        },
    }
    
    const bluePylons = {
        x: [...tempData.pylons.blue.map(e=>e.x)],
        y: [...tempData.pylons.blue.map(e=>e.y)],
        text: [...tempData.pylons.blue.map(e=>e.id)],
        mode: 'lines+markers',
        type: 'scatter',
        name: "Blue Pylons",
        line: {
            color: "#0000ff30"
        },
        marker: {
            color: "#0000ff"
        },
    }
    const interpolatedBluePylons = {
        x: tempData.blueCurved.x,
        y: tempData.blueCurved.y,
        mode: 'lines+markers',
        type: 'scatter',
        name: "Blue Outline",
        line: {
            color: "#00f"
        },
        marker: {
            color: "transparent"
        },
    }
    
    const redPylons = {
        x: [...tempData.pylons.red.map(e=>e.x)],
        y: [...tempData.pylons.red.map(e=>e.y)],
        mode: 'lines+markers',
        type: 'scatter',
        name: "Red Pylons",
        line: {
            color: "#ff000030"
        },
        marker: {
            color: "#f00"
        },
    }
    const interpolatedRedPylons = {
        x: tempData.redCurved.x,
        y: tempData.redCurved.y,
        mode: 'lines+markers',
        type: 'scatter',
        name: "Red Outline",
        line: {
            color: "#f00"
        },
        marker: {
            color: "transparent"
        },
    }
    
    const tempReturn = []
    for(let i=0;i<tempData.neighbours.length;i++){
        tempReturn.push({
            x: [tempData.neighbours[i].x,tempData.neighbours[i].neighbour_same_color.x,tempData.neighbours[i].neighbour_other_color.x,tempData.neighbours[i].x],
            y: [tempData.neighbours[i].y,tempData.neighbours[i].neighbour_same_color.y,tempData.neighbours[i].neighbour_other_color.y,tempData.neighbours[i].y],
            mode: 'lines+markers',
            type: 'scatter',
            name: `Triangle ${i+1}`,
            legend: false,
            line: {
                color: "#303030",
                width: 1
            },
            marker: {
                color: "#303030",
            },
        })
    }
    // tempReturn.push(driveRoute)
    Plotly.newPlot('myDiv', [
        ...tempReturn,
        driveRoute,
        interpolatedDriveRoute,
        bluePylons,
        interpolatedBluePylons,
        redPylons,
        interpolatedRedPylons,
    ], {
        width: 500,
        height: 500,
        autoscale: true,
        plot_bgcolor:"transparent",
        paper_bgcolor:"#202020",
        yaxis: {
            tickcolor: "transparent",
            // tickwidth: 15,
            
            gridcolor: "transparent",
            // gridwidth: 15,
            
            zerolinecolor: "green",
            // zerolinewidth: 2,
        },
        xaxis: {
            tickcolor: "transparent",
            // tickwidth: 50,
            
            gridcolor: "transparent",
            // gridwidth: 2,      
        }
    });
    // rawTraces = data

    // const build = (color,arr) => {
    //     if(!(color in data )) return arr
    //     const x = Object.values(data[color].items).map(e=>e.x)
    //     const z = Object.values(data[color].items).map(e=>e.z)
    //     traces[color].x = x;
    //     traces[color].y = z;

    //     return [[x,...arr[0]],[z,...arr[1]]]
    // }

    // let val = [[],[]]
    // for(let k in traces){
    //     val = build(k,val)
    // }
    // const allx = val[0].sort()
    // const allz = val[1].sort()

    // const distance = 10
    // const point2 = []
    // const pos = data.self.items["0"];
    // // console.log(t,pos.euler)
    // const a = distance * Math.sin(pos.euler.y)
    // const b = distance * Math.cos(pos.euler.y)
    // traces.black.x = [pos.translation.x,pos.translation.x+a]
    // traces.black.y = [pos.translation.z,pos.translation.z+b]

    // plot()

    const html = ["<h2>Known Cones</h2>"]                    
    for(let k in tempData.neighbours){
        const itm = tempData.neighbours[k]
        // if(k==="self") continue;
        // for(let n in data[k].items){
        html.push(`<a data-delete="" href="/delete/${itm.color}:${itm.x}:${itm.y}">${itm.color.padStart(6," ")} ${Math.round(itm.x)} ${Math.round(itm.y)}</a>`)
        // }
    }
    html.push(`<a data-delete="" href="/reset_cones">Delete all</a>`)

    document.getElementById("deletes").innerHTML = html.join("")
    const d = document.querySelectorAll("[data-delete]");
    for(let i=0;i<d.length;i++){
        d[i].addEventListener("click",e=>{
            e.preventDefault();
            fetch(e.target.href)
        })
        // d[i].addEventListener("mouseenter",e=>{
        //     e.preventDefault();
        //     const href = e.target.href.split("/")
        //     const uri = href[href.length - 1].split(":")
        //     const item = rawTraces[uri[0]].items[uri[1]];
        //     traces.selected.x = [item.x]
        //     traces.selected.y = [item.z]
        //     plot()
        // })
        // d[i].addEventListener("mouseleave",e=>{
        //     e.preventDefault();
        //     traces.selected.x = []
        //     traces.selected.y = []
        //     plot()
        // })
    }

    // document.getElementById("details").innerHTML = `Translation:<br />
    // x: ${pos.translation.x}<br />
    // y: ${pos.translation.y}<br />
    // z: ${pos.translation.z}<br />
    // timestamp: ${pos.timestamp}<br />
    // <br />
    // Orientation:<br />
    // x: ${pos.orientation.x}<br />
    // y: ${pos.orientation.y}<br />
    // z: ${pos.orientation.z}<br />
    // w: ${pos.orientation.w}<br />
    // <br />
    // Orientation 2:<br />
    // roll: ${pos.euler.x}<br />
    // pitch: ${pos.euler.y}<br />
    // yaw: ${pos.euler.z}<br />
    // winkel: ${Math.round(pos.euler.y * 180 / Math.PI,2)}<br />`

}

if(!false){
    setInterval(()=>{
        fetch("/positions")
            .then((response) => response.json())
            .then(data=>{
                fillPlot(data)
            })
    },10*1000)
}else{
    fetch("/nearest-neighbour.json")
        .catch(e=>{
            console.log("failed")
        })
        .then((response) => response.json())
        .then(data=>{
            fillPlot(data)
        })
}