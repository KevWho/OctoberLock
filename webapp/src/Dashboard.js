import React, { useEffect } from 'react';
import clsx from 'clsx';
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Drawer from '@material-ui/core/Drawer';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import ListSubheader from '@material-ui/core/ListSubheader';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import IconButton from '@material-ui/core/IconButton';
import Badge from '@material-ui/core/Badge';
import Container from '@material-ui/core/Container';
import Grid from '@material-ui/core/Grid';
import Paper from '@material-ui/core/Paper';
import Link from '@material-ui/core/Link';
import MenuIcon from '@material-ui/icons/Menu';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
import NotificationsIcon from '@material-ui/icons/Notifications';
import { mainListItems, secondaryListItems } from './listItems';
import Chart from './Chart';
import Deposits from './Deposits';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Title from './Title';
import Button from '@material-ui/core/Button';
import ButtonGroup from '@material-ui/core/ButtonGroup';
import TextField from '@material-ui/core/TextField';

const drawerWidth = 240;

const useStyles = makeStyles(theme => ({
  root: {
    display: 'flex',
  },
  toolbar: {
    paddingRight: 24, // keep right padding when drawer closed
  },
  toolbarIcon: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: '0 8px',
    ...theme.mixins.toolbar,
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
  },
  appBarShift: {
    marginLeft: drawerWidth,
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  menuButton: {
    marginRight: 36,
  },
  menuButtonHidden: {
    display: 'none',
  },
  title: {
    flexGrow: 1,
  },
  drawerPaper: {
    position: 'relative',
    whiteSpace: 'nowrap',
    width: drawerWidth,
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  drawerPaperClose: {
    overflowX: 'hidden',
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    width: theme.spacing(7),
    [theme.breakpoints.up('sm')]: {
      width: theme.spacing(9),
    },
  },
  appBarSpacer: theme.mixins.toolbar,
  content: {
    flexGrow: 1,
    height: '100vh',
    overflow: 'auto',
  },
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  paper: {
    padding: theme.spacing(2),
    display: 'flex',
    alignItems: 'center',
    overflow: 'auto',
    flexDirection: 'column',
  },
  fixedHeight: {
    height: 240,
  },
}));

export default function Dashboard() {
  const classes = useStyles();
  const [open, setOpen] = React.useState(true);
  const handleDrawerOpen = () => {
    setOpen(true);
  };
  const handleDrawerClose = () => {
    setOpen(false);
  };
  const fixedHeightPaper = clsx(classes.paper, classes.fixedHeight);

  const [dataChanged, setDataChanged] = React.useState(false)
  const [data, setData] = React.useState({});
  const [stay, setStay] = React.useState({ Entries: [] });
  const [stayName, setStayName] = React.useState("");
  const [newStayName, setNewStayName] = React.useState("");
  const [newStayNum, setNewStayNum] = React.useState(0);
  const selectStay = (name) => {
    setStay(data[name]);
    setStayName(name);
    console.log(stay);
  };

  useEffect(() => {
    setDataChanged(false)
    fetch("https://olock.kevin-hu.org/data")
    .then(response => {
      response.ok ?
        response.json().then(json => {
          let data = json['Airbnb']
          setData(data)
          console.log("Data", data)
        }) : console.log(response)
    })
  }, [dataChanged]);

  const startStay = () => {
    if (stayName != "") {
      fetch('https://olock.kevin-hu.org/stay?type=start&id='+encodeURIComponent(stayName)+'&guestNum=0').then(response => {
        response.ok ?
          response.json().then(json => {
            console.log(json)
            alert(JSON.stringify(json))
          }) : console.log(response)
      });
    } else {
      alert("Select an existing stay")
    }
  };
  const endStay = () => {
    if (stayName != "") {
      fetch('https://olock.kevin-hu.org/stay?type=end&id='+encodeURIComponent(stayName)+'&guestNum=0').then(response => {
        response.ok ?
          response.json().then(json => {
            console.log(json)
            alert(JSON.stringify(json))
          }) : console.log(response)
      });
    } else {
      alert("Select an existing stay")
    }
  };
  const addStay = (event) => {
    event.preventDefault();
    fetch('https://olock.kevin-hu.org/stay?type=add&id='+encodeURIComponent(newStayName)+'&guestNum='+encodeURIComponent(newStayNum)).then(response => {
      response.ok ?
        response.json().then(json => {
          console.log(json)
          alert(JSON.stringify(json))
          setDataChanged(true)
        }) : console.log(response)
    });
    return false
  };

  return (
    <div className={classes.root}>
      <CssBaseline />
      <AppBar position="absolute" className={clsx(classes.appBar, open && classes.appBarShift)}>
        <Toolbar className={classes.toolbar}>
          <IconButton
            edge="start"
            color="inherit"
            aria-label="open drawer"
            onClick={handleDrawerOpen}
            className={clsx(classes.menuButton, open && classes.menuButtonHidden)}
          >
            <MenuIcon />
          </IconButton>
          <Typography component="h1" variant="h6" color="inherit" noWrap className={classes.title}>
            Dashboard
          </Typography>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        classes={{
          paper: clsx(classes.drawerPaper, !open && classes.drawerPaperClose),
        }}
        open={open}
      >
        <div className={classes.toolbarIcon}>
          <IconButton onClick={handleDrawerClose}>
            <ChevronLeftIcon />
          </IconButton>
        </div>
        <Divider />
        <form onSubmit={addStay}>
          <List>
            <ListSubheader inset>New Stay</ListSubheader>
            <ListItem><TextField
              label="Name"
              name="id"
              value={newStayName}
              onChange={event => { setNewStayName(event.target.value) }}
              margin="normal"/></ListItem>
            <ListItem><TextField
              label="Number"
              value={newStayNum}
              onChange={event => { setNewStayNum(event.target.value) }}
              type="number"
              name="guestNum"
              InputLabelProps={{
                shrink: true,
              }}
              margin="normal"/></ListItem>
            <ListItem><Button variant="contained" color="primary" type='submit'>
              Add New Stay
              </Button></ListItem>
          </List>
        </form>
        <Divider />
        <List>
          <div>
            <ListSubheader inset>Recorded Stays</ListSubheader>
            {Object.keys(data).map(key => <ListItem button onClick={() => selectStay(key)}><ListItemText primary={key} /></ListItem>)}
          </div>
        </List>
      </Drawer>
      <main className={classes.content}>
        <div className={classes.appBarSpacer} />
        <Container maxWidth="lg" className={classes.container}>
          <Grid container spacing={3}>
            {/* Butons */}
            <Grid item xs={12}>
              <Paper className={classes.paper} alignItems="center">
                <ButtonGroup
                  color="secondary"
                  size="large"
                  aria-label="large outlined secondary button group"
                >
                  <Button onClick={startStay}>Start</Button>
                  <Button onClick={endStay}>Stop</Button>
                </ButtonGroup>
              </Paper>
            </Grid>
            {/* Chart */}
            <Grid item xs={12}>
              <Paper className={fixedHeightPaper}>
                {/*<img src={"https://olock.kevin-hu.org/plot?id="+stayName} />*/}
                <Chart />
              </Paper>
            </Grid>
            {/* Recent Orders */}
            <Grid item xs={12}>
              <Paper className={classes.paper}>
                <React.Fragment>
                  <Title>Entrances</Title>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell>Num Guests</TableCell>
                        <TableCell>Photo</TableCell>
                        <TableCell>Raw Photo</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {stay.Entries.map(entry => (
                        <TableRow>
                          <TableCell>{entry.TimeStamp}</TableCell>
                          <TableCell>{entry.NumGuests}</TableCell>
                          <TableCell><Link color="primary" href={entry.Photo}>Link</Link></TableCell>
                          <TableCell><Link color="primary" href={entry.Photo}>Link</Link></TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </React.Fragment>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </main>
    </div>
  );
}
