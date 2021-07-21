import React from 'react'
import {Bar, Line, Pie} from 'react-chartjs-2';

export default function PieOS(props) {

    return (
        <div>
            <Pie
                data={props.chartData}
                options={{
                title:{
                    display:props.displayTitle,
                    text:'Largest Cities In '+props.location,
                    fontSize:25
            },
            legend:{
              display:props.displayLegend,
              position:props.legendPosition
            }
          }}
        />
        </div>
    )
}
