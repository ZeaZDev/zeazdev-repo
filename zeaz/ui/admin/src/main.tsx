import {
  Admin,
  Create,
  Datagrid,
  List,
  NumberField,
  NumberInput,
  Resource,
  SimpleForm,
  TextField,
  TextInput,
} from 'react-admin';
import authProvider from '../authProvider';
import dataProvider from './dataProvider';

const TiktokFeedFormCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="product_id" fullWidth />
      <TextInput source="title" fullWidth />
      <NumberInput source="price" />
      <TextInput source="currency" defaultValue="USD" />
      <TextInput source="highlights.0" label="Highlight 1" fullWidth />
      <TextInput source="highlights.1" label="Highlight 2" fullWidth />
      <TextInput source="highlights.2" label="Highlight 3" fullWidth />
    </SimpleForm>
  </Create>
);

const TiktokVideoCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="product_id" fullWidth />
      <TextInput source="script_style" defaultValue="conversion" fullWidth />
      <NumberInput source="duration_seconds" defaultValue={20} />
    </SimpleForm>
  </Create>
);

const TiktokUploadCreate = () => (
  <Create>
    <SimpleForm>
      <TextInput source="job_reference" fullWidth />
      <TextInput source="shop_id" fullWidth />
      <TextInput source="creator_handle" fullWidth />
    </SimpleForm>
  </Create>
);

const TiktokJobsList = () => (
  <List>
    <Datagrid rowClick="show">
      <TextField source="id" />
      <TextField source="type" />
      <TextField source="status" />
      <TextField source="created_at" />
    </Datagrid>
  </List>
);

const AdminPanelList = () => (
  <List>
    <Datagrid>
      <TextField source="role" />
      <TextField source="status" />
      <NumberField source="job_count" />
    </Datagrid>
  </List>
);

const UserPanelList = () => (
  <List>
    <Datagrid>
      <TextField source="id" />
      <TextField source="role" />
      <TextField source="status" />
    </Datagrid>
  </List>
);

export default function App() {
  return (
    <Admin authProvider={authProvider} dataProvider={dataProvider}>
      <Resource name="admin_panel" list={AdminPanelList} options={{ label: 'Admin Control Panel' }} />
      <Resource name="user_panel" list={UserPanelList} options={{ label: 'User Control Panel' }} />
      <Resource name="tiktok_feed_forms" create={TiktokFeedFormCreate} options={{ label: 'Generate Feed Product Form' }} />
      <Resource name="tiktok_videos" create={TiktokVideoCreate} options={{ label: 'Generate Product Video' }} />
      <Resource name="tiktok_uploads" create={TiktokUploadCreate} options={{ label: 'Upload TikTok Shop Aff' }} />
      <Resource name="tiktok_jobs" list={TiktokJobsList} options={{ label: 'TikTok Jobs' }} />
    </Admin>
  );
}
