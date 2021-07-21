import React from 'react'
import UserLoginChart from './UserLoginChart'
export default function UserLogins() {
    const loginData = {
        labels: ['Boston', 'Worcester', 'Springfield', 'Lowell', 'Cambridge', 'New Bedford'],
        datasets:[
          {
            label:'Number of users logged in',
            data:[
              61,
              181,
              153,
              10,
              112,
              92
            ],
            backgroundColor:[
              'rgba(255, 99, 132, 0.6)',
              'rgba(54, 162, 235, 0.6)',
              'rgba(255, 206, 86, 0.6)',
              'rgba(75, 192, 192, 0.6)',
              'rgba(153, 102, 255, 0.6)',
              'rgba(255, 159, 64, 0.6)',
              'rgba(255, 99, 132, 0.6)'
            ]
          }
        ]
      }
    return (
        
        <div>
             <UserLoginChart chartData={loginData} location="Massachusetts" legendPosition="bottom"/>
        </div>
    )
}
