import React from "react";
import querystring from "query-string";

const Posts = ({ match, location }) => {
  const result = querystring.parse(location.search);
  console.log(result);
  return (
    <div>
      <h1>Posts</h1>
      Year: {match.params.year} , Month: {match.params.month}
    </div>
  );
};

export default Posts;
