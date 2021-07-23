import React from 'react'
import PieOS from './PieOS'
export default function OpSysData() {
    const loginData = {
        labels: ['Boston', 'Worcester', 'Springfield'],
        datasets:[
          {
            label:'Number of OS',
            data:[
              61,
              181,
              153
            ],
            backgroundColor:[
              'rgba(255, 99, 132, 0.6)',
              'rgba(54, 162, 235, 0.6)',
              'rgba(255, 206, 86, 0.6)',
            ]
          }
        ]
      }
    return (
        <div>
            <PieOS chartData={loginData}  legendPosition="bottom" />
        </div>
    )
}
