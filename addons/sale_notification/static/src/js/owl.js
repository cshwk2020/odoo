class MyCompoenent extends owl.Component {
  static template = owl.xml`
    <div>
      <t t-foreach="state.data" t-as="data" t-key="data_index">
        <span t-out="data.name"/>
      </t>
    </div>
  setup() {
    this.state = owl.useState({ data: [] })

    this.busService = this.env.services.bus_service
    this.channel = "your_channel"
    this.busService.addChannel(this.channel)
    this.busService.addEventListener("notification", this.onMessage.bind(this))
  }
  onMessage({ detail: notifications }) {
    notifications = notifications.filter(item => item.payload.channel === this.channel)
      notifications.forEach(item => {
          this.state.data.push(item.payload.data)
      })
  }
}
