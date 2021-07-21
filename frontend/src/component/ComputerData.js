import * as React from 'react';
import Link from '@material-ui/core/Link';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Title from './Title';
import { Button, ButtonGroup } from '@material-ui/core';
import {Modal} from 'react-bootstrap';
import './computerRow.css';
const ROWS = [
  {
    "cn": "WS-1",
    "curr_user_source_ip": null,
    "curr_user_source_mac": null,
    "currentuser": null,
    "dnshostname": "ws-1.lab01.local",
    "ip": "192.168.120.134",
    "last_user": [
      "Steel",
      "Steel",
      "Steel",
      "Steel"
    ],
    "last_user_source_ip": [
      "default",
      "default",
      "default",
      "default"
    ],
    "last_user_source_mac": [
      "default",
      "default",
      "default",
      "default"
    ],
    "lastlogon": [
      "11:57:42.49:17-07-2021",
      "12:08:11.19:17-07-2021",
      "12:55:37.28:17-07-2021",
      "12:59:50.45:17-07-2021",
      "13:02:28.01:17-07-2021"
    ],
    "lastlogon_d": "Fri, 16 Jul 2021 10:34:52 GMT",
    "logoff": [
      "11:58:19.15:17-07-2021",
      "12:57:11.47:17-07-2021",
      "13:00:39.79:17-07-2021",
      "13:02:57.26:17-07-2021"
    ],
    "memberof": "[]",
    "monitor": true,
    "operatingsystem": "Windows 10 Enterprise Evaluation",
    "operatingsystemhotfix": "[]",
    "operatingsystemservicepack": "[]",
    "operatingsystemversion": "10.0 (19043)"
  },
  {
    "cn": "WS-2",
    "dnshostname": "WS-2.lab02.local",
    "ip": "192.168.120.130",
    "lastlogon_d": "Thu, 15 Jul 2021 22:29:04 GMT",
    "memberof": "[]",
    "monitor": false,
    "operatingsystem": "Windows 10 Enterprise Evaluation",
    "operatingsystemhotfix": "[]",
    "operatingsystemservicepack": "[]",
    "operatingsystemversion": "10.0 (19043)"
  }
]

function preventDefault(event) {
  event.preventDefault();
}

export default function ComputerData() {
  let labs=[];
  const [selectedLab,setSelectedLab]=React.useState();
  const [selectedComputer,setSelectedComputer]=React.useState();

  ROWS.forEach(row=>{
    if(!labs.includes(row.dnshostname)){
      labs.push(row.dnshostname)
    }

  })
  console.log(selectedComputer)
  return (
    <React.Fragment>
      <Modal show={!!selectedComputer} onHide={()=>setSelectedComputer(undefined)} centered>
        <Modal.Header>{selectedComputer?.cn}</Modal.Header>
        <Modal.Body>
          <table>
            {selectedComputer&&Object.keys(selectedComputer).map(key=><tr>
              <td>{key}</td>
              <td>{selectedComputer[key]}</td>
            </tr>)}
          </table>
          {selectedComputer?.toString()}
        </Modal.Body>
      </Modal>
      <Title>Computers</Title>
      <ButtonGroup variant="contained" color="primary" aria-label="contained primary button group">
      {!selectedLab&&labs.map(lab=>(
          <Button onClick={()=>setSelectedLab(lab)}>{lab}</Button>
      ))}
      </ButtonGroup>
      {selectedLab&&<Button variant="outlined" color="secondary" onClick={()=>setSelectedLab(undefined)}>CLEAR</Button>}
      {selectedLab&&
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>IP</TableCell>
            <TableCell>LAST LOGON</TableCell>
            <TableCell>MONITOR</TableCell>
            <TableCell>OS</TableCell>
            <TableCell>DNS HOST NAME</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {ROWS.filter(row=>row.dnshostname===selectedLab).map((row) => (
              <TableRow className={row.monitor?"monitor-on":""} key={row.cn} onClick={row.monitor?()=>{
                setSelectedComputer(row)}:null}>
                  <TableCell className={row.monitor?"monitor-on":""}>{row.ip}</TableCell>
                  <TableCell className={row.monitor?"monitor-on":""}>{row.lastlogon}</TableCell>
                  <TableCell className={row.monitor?"monitor-on":""}>{row.monitor?"TRUE":"FALSE"}</TableCell>
                <TableCell className={row.monitor?"monitor-on":""}>{row.operatingsystem}</TableCell>
                <TableCell className={row.monitor?"monitor-on":""}>{row.dnshostname}</TableCell>
              </TableRow>
          ))}
        </TableBody>
      </Table>}

      <Link color="primary" href="#" onClick={preventDefault} sx={{ mt: 3 }}>
      </Link>
    </React.Fragment>
  );
}
