import React, { Component } from "react";

// This will be a controlled component -- Meaning it will rely on the props from it's parent
class Counter extends Component {
  // We can use this to decide if we want to make an ajax call to the server based on the changes to props and state objects
  componentDidUpdate(prevProps, prevState) {
    console.log("prevProps", prevProps);
    console.log("prevState", prevState);
    if (prevProps.counter.value !== this.props.counter.value) {
      // Ajax call and get new data from the server
    }
  }

  // This is called before the change is made to state, so we have an opportunity to do any kind of cleanup
  // So if you have set up timers or listeners, we can clean those up before this state changes; to prevent memory leaks
  // --- seems kinda important ---
  componentWillUnmount() {
    /* An example I can think of off the top of my head:
        We have a timer that refreshes something every minute while this state is active.
        State change happens at 1 second after last refresh.
        Timer will continue for 59 seconds until it completes, unless we tell it to stop here.
    */
    console.log("Counter - Unmount");
  }

  render() {
    console.log("Counter - Rendered");
    const { onIncrement, onDelete, counter } = this.props;
    return (
      // React.Fragment is in place of div, because this element will already be wrapped in a div, and this will not create a second
      <div>
        <span className={this.getBadgeClasses()}>{this.formatCount()}</span>
        <button // Can swap out { key: 1 } with a variable for a product
          onClick={() => onIncrement(counter)}
          className="btn btn-secondary btn-sm"
        >
          Increment
        </button>
        <button
          onClick={() => onDelete(counter.id)}
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
    classes += this.props.counter.value === 0 ? "warning" : "primary";
    return classes;
  }

  formatCount() {
    const { value: count } = this.props.counter;
    return count === 0 ? "Zero" : count;
  }
}

export default Counter;
