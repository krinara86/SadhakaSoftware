// Initialize Firebase
// TODO: replace with your own Firebase config
var firebaseConfig = {
  apiKey: "AIzaSyD2Qv-8dC9atWBU_IFWXmxsGSp5T-_FOtM",
  authDomain: "sadhakacustomizer.firebaseapp.com",
  projectId: "sadhakacustomizer",
  storageBucket: "sadhakacustomizer.appspot.com",
  messagingSenderId: "401905258509",
  appId: "1:401905258509:web:cd9661bbe700b04fa00544"
};
firebase.initializeApp(firebaseConfig);
var db = firebase.firestore();

new Vue({
    el: '#app',
    data: {
      search: '',
      selectedSadhaka: { 
        name: '',
        assignedAsanas: [],
        dietAndAdditionalNotes: '' 
      },
      sadhakas: [],
      asanas: []
    },
  computed: {
    filteredSadhakas() {
      return this.sadhakas.filter(sadhaka => sadhaka.name.includes(this.search));
    }
  },
  methods: {
    selectSadhaka(sadhaka) {
      this.selectedSadhaka = JSON.parse(JSON.stringify(sadhaka)); // deep copy
    },
    deleteAsana(index) {
      this.selectedSadhaka.assignedAsanas.splice(index, 1);
    },
    addAsana() {
      this.selectedSadhaka.assignedAsanas.push({asanaName: '', practiceday: '', specialnotes: '', reps: ''});
    },
    async saveSadhaka() {
      const { name } = this.selectedSadhaka;
      const sadhaka = this.sadhakas.find(sadhaka => sadhaka.name === name);

      if (sadhaka) {
        // update existing sadhaka
        await db.collection('sadhakas').doc(name).update(this.selectedSadhaka);
      } else {
        // add new sadhaka
        await db.collection('sadhakas').doc(name).set(this.selectedSadhaka);
      }

      this.loadSadhakas();
    },
    suggestAsana(index) {
      // implement autocomplete for AsanaName here
    },
    async loadSadhakas() {
      const querySnapshot = await db.collection('sadhakas').get();
      this.sadhakas = querySnapshot.docs.map(doc => doc.data());
    },
    async loadAsanas() {
      const response = await fetch('https://github.com/krinara86/Program-Customizer/blob/main/asanas.json');
      const asanas = await response.json();
      this.asanas = asanas;
    }
  },
  created() {
    this.loadSadhakas();
    this.loadAsanas();
  }
});
