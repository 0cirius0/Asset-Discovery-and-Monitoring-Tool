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
export default function Users() {
    const [selectedLab,setSelectedLab]=React.useState();
    const [selectedUser,setSelectedUser]=React.useState();
    const labs = []
    const users = [
        {"_id":{"$oid":"60f2c3f8ecafe72018129746"},
        "name":"Stella",
        "memberof":"['CN=Group Policy Creator Owners,CN=Users,DC=lab01,DC=local', 'CN=Domain Admins,CN=Users,DC=lab01,DC=local', 'CN=Enterprise Admins,CN=Users,DC=lab01,DC=local', 'CN=Schema Admins,CN=Users,DC=lab01,DC=local', 'CN=Administrators,CN=Builtin,DC=lab01,DC=local']",
        "userprincipalname":"gurl@lab01.local"},
        {"_id":{"$oid":"60f2c3f8ecafe72018129747"},
        "name":"Harve Init",
        "memberof":"[]",
        "userprincipalname":"init@lab01.local"},
        {"_id":{"$oid":"60f2c3f8ecafe72018129745"},
        "name":"Adam Steele",
        "memberof":"CN=RDPUsers,CN=Users,DC=lab01,DC=local",
        "userprincipalname":"steel@lab01.local",
        "current_device":"null",
        "lastlogon":["13:02:28.01:17-07-2021"],
        "last_device":["WS-1"]},
        {"_id":{"$oid":"60f2c3f8ecafe72018129748"},
        "name":"SQL Database",
        "memberof":"[]",
        "userprincipalname":"sql@lab01.local"}
    ]

    users.forEach(user=>{
        if(!labs.includes(domain(user.userprincipalname))){
          labs.push(domain(user.userprincipalname))
        }
    
      })
    return (
        <div>
        
      <Modal show={!!selectedUser} onHide={()=>setSelectedUser(undefined)} centered>
        <Modal.Header>{selectedUser?.name}</Modal.Header>
        <Modal.Body>
          <table>
            {selectedUser&&Object.keys(selectedUser).map(key=><tr>
              <td>{key}</td>
              <td>{selectedUser[key]}</td>
            </tr>)}
          </table>
          {selectedUser?.toString()}
        </Modal.Body>
      </Modal>
  
      <ButtonGroup variant="contained" color="primary" aria-label="contained primary button group">
      {labs.map(lab => (
          <Button onClick= {() => {setSelectedLab(lab)}}>{lab}</Button>
      ))}
      </ButtonGroup>
      {selectedLab&&<Button variant="outlined" color="secondary" onClick={()=>setSelectedLab(undefined)}>CLEAR</Button>} 
      {selectedLab&&
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
            <TableCell>Principal Name</TableCell>
            
          </TableRow>
        </TableHead>
        <TableBody>
          {users.filter(row =>  domain(row.userprincipalname) === selectedLab).map((row) => (
              <TableRow className="monitor-on" key={row.name} onClick={()=>{setSelectedUser(row)}}>
                  <TableCell className="monitor-on">{row.name}</TableCell>
                <TableCell className="monitor-on">{row.userprincipalname}</TableCell>
               
              </TableRow>
          ))}
        </TableBody>
      </Table>}

    
    
        </div>
    )
}
function preventDefault(event) {
    event.preventDefault();
}

function domain(str){
    
    let i = 0;
    for (var k = 0; k<str.length; k++){
        console.log(str.charAt(k));
    
        if(str.charAt(k) === '@'){
        break;
        }
    }
    return str.substr(k+1, str.length);

}