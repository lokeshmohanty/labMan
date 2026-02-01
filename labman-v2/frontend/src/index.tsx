import { render } from 'solid-js/web';
import App from './App';
import './styles/index.css';
import './styles/common.css';

const root = document.getElementById('root');

if (root) {
    render(() => <App />, root);
}
