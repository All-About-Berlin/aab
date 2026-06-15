import React from 'react';
import { Link } from 'gatsby';

const Guides = () => (
  <div>
    <h1>Guides</h1>
    <ul>
      <li><Link to="/guides/german-brokers">German Brokers for Trading and Investments</Link></li>
      {/* Add other guides here */}
    </ul>
  </div>
);

export default Guides;