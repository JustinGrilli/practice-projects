import React, { Component } from "react";

class Counter extends Component {
  state = {
    value: this.props.counter.value
  };

  handleIncrement = () => {
    // setState updates the state of the component
    this.setState({ value: this.state.value + 1 });
  };

  render() {
    return (
      // React.Fragment is in place of div, because this element will already be wrapped in a div, and this will not create a second
      <div>
        <span className={this.getBadgeClasses()}>{this.formatCount()}</span>
        <button // Can swap out { key: 1 } with a variable for a product
          onClick={this.handleIncrement}
          className="btn btn-secondary btn-sm"
        >
          Increment
        </button>
        <button
          onClick={() => this.props.onDelete(this.props.counter.id)}
          className="btn btn-danger btn-sm m-2"
        >
          Delete
        </button>
      </div>
    );
  }

  getBadgeClasses() {
    let classes = "badge m-2 badge-";
    // If the count is 0 then highlight yellow, otherwise highlight blue
    classes += this.state.value === 0 ? "warning" : "primary";
    return classes;
  }

  formatCount() {
    const { value: count } = this.state;
    return count === 0 ? "Zero" : count;
  }
}

export default Counter;
