import { Admin, Resource } from 'react-admin';
import authProvider from '../authProvider';

export default function App() {
  return (
    <Admin authProvider={authProvider} dataProvider={undefined as never}>
      <Resource name="wallet" />
      <Resource name="ledger" />
    </Admin>
  );
}
